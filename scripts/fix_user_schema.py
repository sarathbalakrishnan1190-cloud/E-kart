import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.getenv("DATABASE_URL")
if not url:
    raise SystemExit("DATABASE_URL is missing")

engine = create_engine(url)

with engine.begin() as conn:
    columns = conn.execute(
        text(
            "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
        )
    ).fetchall()
    print("BEFORE:", columns)

    conn.execute(text("ALTER TABLE users ALTER COLUMN password DROP NOT NULL"))

    columns_after = conn.execute(
        text(
            "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
        )
    ).fetchall()
    print("AFTER:", columns_after)
