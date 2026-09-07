from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.post("/items")
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # 1. Find the user's cart
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    # 2. If the user doesn't have a cart, create one
    if cart is None:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    # 3. Check whether the product exists
    product = db.get(Product, item.product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # 4. Check whether this product is already in the cart
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()

    # 5. If already there, increase quantity
    if cart_item:
        cart_item.quantity += item.quantity

    # 6. Otherwise create a new CartItem
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return cart_item


@router.get("/")
def get_my_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    return cart

@router.put("/items/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cart_item = db.get(CartItem, cart_item_id)

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    # Make sure this cart item belongs to the logged-in user
    if cart_item.cart.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to modify this cart item"
        )

    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    cart_item.quantity = item.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item

@router.delete("/items/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cart_item = db.get(CartItem, cart_item_id)

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    if cart_item.cart.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to remove this cart item"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Item removed from cart"
    }

@router.post("/checkout")
def checkout(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Find user's cart
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    # 2. Make sure cart has items
    if not cart.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_price = 0.0

    # 3. Check products and stock
    for cart_item in cart.items:
        product = db.get(Product, cart_item.product_id)

        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {cart_item.product_id} not found"
            )

        if cart_item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.id}"
            )

        total_price += product.price * cart_item.quantity

    # 4. Create Order
    new_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status="pending"
    )

    db.add(new_order)
    db.flush()

    # 5. Create OrderItems + reduce stock
    for cart_item in cart.items:
        product = db.get(Product, cart_item.product_id)

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=product.price
        )

        db.add(order_item)

        product.stock -= cart_item.quantity

    # 6. Clear cart
    for cart_item in cart.items:
        db.delete(cart_item)

    # 7. Save everything
    db.commit()
    db.refresh(new_order)

    return new_order