from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Use PostgreSQL or SQLite based on settings
if settings.USE_POSTGRES and settings.SQLALCHEMY_DATABASE_URI:
    # Use PostgreSQL if configured
    db_uri = str(settings.SQLALCHEMY_DATABASE_URI)
    print(f"Using PostgreSQL database: {db_uri}")
else:
    # Use SQLite as fallback
    db_uri = "sqlite:///./app.db"
    print(f"Using SQLite database: {db_uri}")

# Create engine with appropriate configuration for SQLite
connect_args = {"check_same_thread": False} if db_uri.startswith("sqlite") else {}
engine = create_engine(db_uri, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)