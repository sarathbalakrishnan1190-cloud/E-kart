from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    owner = relationship(
    "User",
    back_populates="products"
    )
    order_items = relationship(
    "OrderItem",
    back_populates="product"
    )

    cart_items = relationship(
    "CartItem",
    back_populates="product"
)