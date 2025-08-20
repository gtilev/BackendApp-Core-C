import os
import pytest
from typing import Dict, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import SessionLocal, get_db
from app.core.config import settings
from app.app import models
from app.core.security import get_password_hash
from app.main import app


# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a fresh database for each test.
    """
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Run the tests
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    # Drop the tables after the test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Create a test client for testing API endpoints.
    """
    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: db
    
    # Create a test client
    with TestClient(app) as c:
        yield c
    
    # Reset dependency overrides
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_user(db) -> models.User:
    """
    Create a test user in the database.
    """
    user = models.User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def user_token_headers(client, test_user) -> Dict[str, str]:
    """
    Create authorization headers for a test user.
    """
    # Get a token for the test user
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    response = client.post("/api/auth/login", data=login_data)
    tokens = response.json()
    a_token = tokens["access_token"]
    
    # Create and return the authorization headers
    return {"Authorization": f"Bearer {a_token}"}