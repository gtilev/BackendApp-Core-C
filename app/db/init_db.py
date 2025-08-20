from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine

from app.db.session import engine
from app.db.base import Base  # This imports all models


def init_db():
    """
    Initialize the database by creating all tables if they don't exist.
    This should be called when the application starts.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")