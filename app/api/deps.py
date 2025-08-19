from typing import Generator
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator:
    """
    Dependency for getting the database session
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()