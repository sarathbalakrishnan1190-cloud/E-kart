from app.models.order_item import OrderItem
from app.models.product import Product


def create_order_items(new_order, db):
    for item in new_order.items:
        product = db.get(Product, item.product_id)

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)