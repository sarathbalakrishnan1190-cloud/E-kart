from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

# Which order does this item belong to?
    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

     # Which product was purchased?
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    # How many were purchased?
    quantity = Column(
        Integer,
        nullable=False
    )

     # Price at the time of purchase
    price = Column(
        Float,
        nullable=False
    )

    # Relationship with Order
    order = relationship(
        "Order",
        back_populates="items"
    )
    # Relationship with Product
    product = relationship(
    "Product",
    back_populates="order_items"
    )