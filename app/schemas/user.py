from typing import Optional
from pydantic import BaseModel


class UserDisabled(BaseModel):
    """
    Schema representing disabled user functionality
    """
    status: str = "disabled"
    message: str = "User authentication has been disabled"


# Basic user information (for backward compatibility)
class User(BaseModel):
    """
    Minimal user schema for backward compatibility
    """
    id: Optional[int] = None
    username: Optional[str] = None
    
    class Config:
        orm_mode = True