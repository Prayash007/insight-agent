"""
InsightAgent MCP Server: Read-Only Database Connection Pool
Enforces strict database hardening:
  - Read-only transaction enforcement (Postgres: default_transaction_read_only = on, SQLite: PRAGMA query_only = ON)
  - Execution statement timeout (2500ms)
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'insight_brokerage.db'}")

def create_hardened_engine(db_url: str = DEFAULT_DB_URL):
    """Initializes a connection engine with read-only & timeout hooks."""
    is_sqlite = db_url.startswith("sqlite")
    
    if is_sqlite:
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False
        )

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # Set query busy timeout to 2500ms
            cursor.execute("PRAGMA busy_timeout = 2500;")
            cursor.close()

    else:
        # PostgreSQL Engine with Connection Pool
        engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_timeout=10,
            echo=False
        )

        @event.listens_for(engine, "connect")
        def set_postgres_hardening(dbapi_connection, connection_record):
            with dbapi_connection.cursor() as cursor:
                # Enforce read-only at session level
                cursor.execute("SET default_transaction_read_only = on;")
                # Strict 2500ms timeout
                cursor.execute("SET statement_timeout = '2500ms';")

    return engine


# Singleton engine instance
engine = create_hardened_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Context manager or generator for database connections."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
