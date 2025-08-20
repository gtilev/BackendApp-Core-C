# Re-export all schemas to make imports cleaner
from app.schemas.token import AuthDisabled
from app.schemas.user import User, UserDisabled
from app.schemas.operation import Operation, OperationCreate, OperationList
from app.schemas.file import File, FileCreate, FileList, FileWithOperationCount

# For backward compatibility
Token = AuthDisabled
TokenPayload = AuthDisabled
UserCreate = UserDisabled
UserUpdate = UserDisabled
UserInDB = User