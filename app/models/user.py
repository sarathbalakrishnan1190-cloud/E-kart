from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    products = relationship(
    "Product",
    back_populates="owner"
    )

    orders = relationship(
        "Order",
        back_populates="user"
    )

    cart = relationship(
        "Cart",
        back_populates="user",
        uselist=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="customer",
        nullable=False
    )