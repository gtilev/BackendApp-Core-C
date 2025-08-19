from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class FileBase(BaseModel):
    filename: str
    template_type: str


# Properties to receive via API on creation
class FileCreate(FileBase):
    file_path: str


# Properties to receive via API on update
class FileUpdate(FileBase):
    processed: Optional[bool] = None


# Properties shared by models stored in DB
class FileInDBBase(FileBase):
    id: int
    upload_date: datetime
    processed: bool
    file_path: str
    
    class Config:
        orm_mode = True


# Properties to return via API
class File(FileInDBBase):
    pass


# Additional properties to return via API
class FileWithOperationCount(File):
    operation_count: int


# Properties for pagination
class FileList(BaseModel):
    items: List[File]
    total: int