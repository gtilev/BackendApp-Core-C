from typing import Optional
from pydantic import BaseModel


class AuthDisabled(BaseModel):
    """
    Schema representing disabled authentication
    """
    status: str = "disabled"
    message: str = "Authentication functionality has been disabled"