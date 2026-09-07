# Ecom

This project is a basic ecommerce backend built with FastAPI and SQLAlchemy.

## Project structure

- app/ - application code
- app/models/ - SQLAlchemy models
- app/schemas/ - Pydantic schemas
- app/routes/ - API routes
- alembic/ - Alembic migrations

## Setup

1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   - Windows: .venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   uvicorn app.main:app --reload

## Default database

By default, the app uses a local SQLite database file named `ecommerce.db`.

## Notes

This is a starter structure for an ecommerce backend and can be extended with authentication, orders, payments, and migrations.
