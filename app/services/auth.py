from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Get a user by username
    """
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user by username and password
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_user(db: Session, user_in: schemas.user.UserCreate) -> models.User:
    """
    Create a new user
    """
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, db_user: models.User, user_in: schemas.user.UserUpdate
) -> models.User:
    """
    Update a user
    """
    update_data = user_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user