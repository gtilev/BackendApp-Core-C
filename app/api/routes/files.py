import io
import os
import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.app import models, schemas
from app.api import deps
from app.core.config import settings
from app.services.file_processor import FileProcessor
from app.services.template_detector import TemplateDetector
from app.services.s3 import S3Service

router = APIRouter(tags=["files"])


@router.post("/upload", 
            response_model=schemas.file.File,
            summary="Upload a new file",
            description="Upload an Excel file to S3 storage and detect its template type")
async def upload_file(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload an Excel file for processing accounting operations.
    """
    # Validate file extension
    if not file.filename.endswith(('.xls', '.xlsx')):
        print(f"[ERROR] Invalid file format: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only Excel files (.xls, .xlsx) are supported."
        )
    
    print(f"[DEBUG] Processing file upload: {file.filename}")
    
    # Read file content
    contents = await file.read()
    print(f"[DEBUG] File content read, size: {len(contents)} bytes")
    
    # Create a BytesIO object for in-memory file processing
    file_obj = io.BytesIO(contents)
    
    # Detect template type
    print(f"[DEBUG] Starting template detection for file: {file.filename}")
    template_detector = TemplateDetector()
    template_type = template_detector.detect_template_from_bytes(file_obj)
    
    print(f"[DEBUG] Template detection result: {template_type}")
    
    if not template_type:
        print(f"[ERROR] Could not recognize template format for file: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not recognize Excel template format."
        )
    
    # Generate a unique S3 object key
    s3_key = f"{uuid.uuid4()}-{file.filename}"
    
    # Upload to S3
    s3_service = S3Service()
    success, message = s3_service.upload_file(contents, s3_key)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to storage: {message}"
        )
    
    # Create file record in database
    file_processor = FileProcessor(db)
    db_file = file_processor.create_file(
        filename=file.filename,
        template_type=template_type.value,
        file_path=s3_key  # Store S3 key instead of local path
    )
    
    return db_file


@router.post("/{file_id}/process", response_model=schemas.operation.OperationList,
            summary="Process a file", description="Extract accounting operations from an uploaded file")
def process_file(
    *,
    db: Session = Depends(deps.get_db),
    file_id: int
) -> Any:
    """
    Process an uploaded file to extract accounting operations.
    """
    # Check if file exists
    file = db.query(models.UploadedFile).filter(
        models.UploadedFile.id == file_id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file has already been processed
    if file.processed:
        # Get existing operations
        operations = db.query(models.AccountingOperation).filter(
            models.AccountingOperation.file_id == file_id
        ).all()
        
        return {"items": operations, "total": len(operations)}
    
    # Process the file
    file_processor = FileProcessor(db)
    operations = file_processor.process_file(file_id)
    
    if not operations:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process file"
        )
    
    # Get saved operations from database (to ensure we have the IDs)
    db_operations = db.query(models.AccountingOperation).filter(
        models.AccountingOperation.file_id == file_id
    ).all()
    
    return {"items": db_operations, "total": len(db_operations)}


@router.get("/", response_model=schemas.file.FileList,
           summary="List files", description="Get a list of all uploaded files with filtering options")
def get_files(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    template_type: str = None,
    processed: bool = None
) -> Any:
    """
    Retrieve files with filtering and pagination.
    """
    query = db.query(models.UploadedFile)
    
    # Apply filters if provided
    if template_type:
        query = query.filter(models.UploadedFile.template_type == template_type)
    
    if processed is not None:
        query = query.filter(models.UploadedFile.processed == processed)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    files = query.order_by(models.UploadedFile.upload_date.desc()).offset(skip).limit(limit).all()
    
    return {"items": files, "total": total}


@router.get("/{file_id}", response_model=schemas.file.FileWithOperationCount,
           summary="Get file details", description="Get detailed information about a specific file")
def get_file(
    *,
    db: Session = Depends(deps.get_db),
    file_id: int
) -> Any:
    """
    Get detailed information about a specific file.
    """
    # Get file with operation count
    file = db.query(
        models.UploadedFile,
        func.count(models.AccountingOperation.id).label("operation_count")
    ).join(
        models.AccountingOperation,
        models.UploadedFile.id == models.AccountingOperation.file_id,
        isouter=True
    ).filter(
        models.UploadedFile.id == file_id
    ).group_by(models.UploadedFile.id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    result = file[0].__dict__
    result["operation_count"] = file[1]
    
    return result


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None,
              summary="Delete file", description="Delete a file from S3 storage and database")
def delete_file(
    *,
    db: Session = Depends(deps.get_db),
    file_id: int
) -> None:
    """
    Delete a file and its associated operations.
    """
    file = db.query(models.UploadedFile).filter(
        models.UploadedFile.id == file_id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete the file from S3 if it exists
    if file.file_path:
        try:
            s3_service = S3Service()
            s3_service.delete_file(file.file_path)
        except Exception as e:
            print(f"Error deleting file {file.file_path} from S3: {e}")
    
    # Delete the database record (cascade will delete operations)
    db.delete(file)
    db.commit()