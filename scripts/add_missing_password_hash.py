import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.getenv("DATABASE_URL")
if not url:
    raise SystemExit("DATABASE_URL is missing in .env")

engine = create_engine(url)

with engine.begin() as conn:
    current_columns = [
        row[0]
        for row in conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY column_name")
        )
    ]
    print("CURRENT_COLUMNS=", current_columns)

    if "password_hash" not in current_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
        print("ADDED password_hash")

    if "password" in current_columns:
        conn.execute(
            text(
                "UPDATE users SET password_hash = password WHERE password_hash IS NULL AND password IS NOT NULL"
            )
        )
        print("COPIED password values to password_hash")

    final_columns = [
        row[0]
        for row in conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY column_name")
        )
    ]
    print("FINAL_COLUMNS=", final_columns)
