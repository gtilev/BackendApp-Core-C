"""
Re-export models and schemas for consistent imports across the application.
"""
# Import models and create a namespace
import app.models.user
import app.models.file
import app.models.operation

# Create a models namespace
class models:
    User = app.models.user.User
    UploadedFile = app.models.file.UploadedFile
    AccountingOperation = app.models.operation.AccountingOperation

# Import and re-export schemas
from app.schemas.file import File, FileCreate, FileList, FileWithOperationCount
from app.schemas.user import User as UserSchema, UserDisabled
from app.schemas.operation import Operation, OperationCreate, OperationList
from app.schemas.token import AuthDisabled

# For backward compatibility
UserCreate = UserDisabled
UserUpdate = UserDisabled
UserInDB = UserSchema
Token = AuthDisabled
TokenPayload = AuthDisabled

# Create a schemas namespace
class schemas:
    class file:
        File = File
        FileCreate = FileCreate
        FileList = FileList
        FileWithOperationCount = FileWithOperationCount
    
    class user:
        User = UserSchema
        UserCreate = UserCreate
        UserUpdate = UserUpdate
        UserInDB = UserInDB
    
    class operation:
        Operation = Operation
        OperationCreate = OperationCreate
        OperationList = OperationList
    
    class token:
        Token = Token
        TokenPayload = TokenPayload