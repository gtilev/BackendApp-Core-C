from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.get("/status", summary="Auth status", description="Authentication status")
def auth_status() -> dict:
    """
    Return authentication status (authentication is disabled)
    """
    return {
        "authentication": "disabled",
        "message": "Authentication and user management have been disabled"
    }