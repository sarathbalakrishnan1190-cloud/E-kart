
"""add orders and order items

Revision ID: ce010210a376
Revises: b1824e371c31
Create Date: 2026-08-27 12:00:17.941847

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ce010210a376"
down_revision: Union[str, Sequence[str], None] = "b1824e371c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # 1. Give existing products an owner
    # ---------------------------------------------------------

    op.execute(
        sa.text(
            """
            UPDATE products
            SET owner_id = (SELECT MIN(id) FROM users)
            WHERE owner_id IS NULL
            """
        )
    )

    # Make owner_id required
    op.alter_column(
        "products",
        "owner_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 2. Create orders table
    # ---------------------------------------------------------

    op.create_table(
        "orders",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),

        sa.Column(
            "total_price",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="pending",
        ),
    )

    # ---------------------------------------------------------
    # 3. Create order_items table
    # ---------------------------------------------------------

    op.create_table(
        "order_items",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id"),
            nullable=False,
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "price",
            sa.Float(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove order_items first because it depends on orders/products
    op.drop_table("order_items")

    # Remove orders
    op.drop_table("orders")

    # Make owner_id nullable again
    op.alter_column(
        "products",
        "owner_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

