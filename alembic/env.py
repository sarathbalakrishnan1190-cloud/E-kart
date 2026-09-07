from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from app.models.order_item import OrderItem
from alembic import context
from app.models.order import Order

from app.database import Base, DATABASE_URL
from app.models.user import User
from app.models.product import Product


# Alembic Config object
config = context.config
print("ALEMBIC DATABASE URL:", config.get_main_option("sqlalchemy.url"))
print("DATABASE_URL FROM ENV:", DATABASE_URL)

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Tell Alembic where the database is
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


# Tell Alembic about our SQLAlchemy models
target_metadata = Base.metadata