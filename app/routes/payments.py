from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.auth import get_current_user


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/create/{order_id}")
def create_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find the order
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 2. Make sure the order belongs to the logged-in user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot pay for this order"
        )

    # 3. Make sure payment doesn't already exist
    if order.payment is not None:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists for this order"
        )

    # 4. Create a fake payment ID
    fake_payment_id = f"PAY_{uuid4().hex[:10].upper()}"

    # 5. Create payment
    payment = Payment(
        order_id=order.id,
        payment_id=fake_payment_id,
        amount=order.total_price,
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment created",
        "payment_id": payment.payment_id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status
    }

@router.post("/pay/{payment_id}")
def process_payment(
    payment_id: str,
    success: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find the payment
    payment = db.query(Payment).filter(
        Payment.payment_id == payment_id
    ).first()

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    # 2. Find the related order
    order = db.get(Order, payment.order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 3. Check ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot process this payment"
        )

    # 4. Make sure payment is pending
    if payment.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Payment has already been processed"
        )

    # 5. Simulate payment result
    if success:
        payment.status = "success"
        order.status = "confirmed"

        message = "Payment successful"

    else:
        payment.status = "failed"

        message = "Payment failed"

    # 6. Save changes
    db.commit()

    db.refresh(payment)
    db.refresh(order)

    return {
        "message": message,
        "payment_id": payment.payment_id,
        "payment_status": payment.status,
        "order_id": order.id,
        "order_status": order.status
    }