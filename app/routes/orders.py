
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.tasks import send_order_notification

from app.database import get_db
from app.schemas.order import (
    OrderCreate,
    OrderRead,
    OrderStatusUpdate
)

from app.auth import get_current_user, require_admin


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/", response_model=OrderRead)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    total_price = 0.0

    for item in order_data.items:
        product = db.get(Product, item.product_id)

        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        if item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.id}"
            )

        total_price += product.price * item.quantity

    new_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status="pending"
    )

    db.add(new_order)
    db.flush()

    for item in order_data.items:
        product = db.get(Product, item.product_id)

        product.stock -= item.quantity

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)

    db.commit()
    db.refresh(new_order)

    send_order_notification.delay(new_order.id)

    return new_order


@router.get("/")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()

    return orders


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@router.delete("/{order_id}")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to cancel this order"
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be cancelled"
        )

    for item in order.items:
        product = db.get(Product, item.product_id)

        if product:
            product.stock += item.quantity

    order.status = "cancelled"

    db.commit()
    db.refresh(order)

    return {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "status": order.status
    }


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_statuses = {
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled"
    }

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    valid_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["shipped"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": []
    }

    if status_data.status not in valid_transitions[order.status]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change order from "
                f"{order.status} to {status_data.status}"
            )
        )

    order.status = status_data.status

    db.commit()
    db.refresh(order)

    return order

