import os
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def main():
    uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not uri:
        return

    engine = create_engine(uri)

    timeout = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
    interval = int(os.getenv("DB_WAIT_INTERVAL", "2"))

    deadline = time.time() + timeout
    while True:
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("[wait_for_db] Database connection ready.")
            return
        except OperationalError:
            if time.time() > deadline:
                raise RuntimeError("Database is not ready after waiting.") from None
            print("[wait_for_db] Waiting for database...", flush=True)
            time.sleep(interval)


if __name__ == "__main__":
    main()
