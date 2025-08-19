from fastapi import HTTPException, status


class AccountingAPIException(HTTPException):
    """Base exception class for accounting API"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class CredentialsException(AccountingAPIException):
    """Exception raised for authentication errors"""
    
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(AccountingAPIException):
    """Exception raised for permission errors"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(AccountingAPIException):
    """Exception raised when a resource is not found"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class BadRequestException(AccountingAPIException):
    """Exception raised for bad requests"""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ExcelParsingException(BadRequestException):
    """Exception raised when Excel parsing fails"""
    
    def __init__(self, detail: str = "Failed to parse Excel file"):
        super().__init__(detail=detail)


class TemplateDetectionException(BadRequestException):
    """Exception raised when template detection fails"""
    
    def __init__(self, detail: str = "Failed to detect Excel template"):
        super().__init__(detail=detail)