import os
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.app import models, schemas
from app.api import deps
from app.core.config import settings
from app.services.file_processor import FileProcessor
from app.services.template_detector import TemplateDetector

router = APIRouter()


@router.post("/upload", response_model=schemas.file.File)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only Excel files (.xls, .xlsx) are supported."
        )
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    # Save file to disk
    file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Detect template type
    template_detector = TemplateDetector()
    template_type = template_detector.detect_template(file_path)
    
    if not template_type:
        os.remove(file_path)  # Clean up file if template not recognized
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not recognize Excel template format."
        )
    
    # Create file record in database
    file_processor = FileProcessor(db)
    db_file = file_processor.create_file(
        filename=file.filename,
        template_type=template_type.value,
        file_path=file_path
    )
    
    return db_file


@router.post("/{file_id}/process", response_model=schemas.operation.OperationList)
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


@router.get("/", response_model=schemas.file.FileList)
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


@router.get("/{file_id}", response_model=schemas.file.FileWithOperationCount)
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


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
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
    
    # Delete the physical file if it exists
    if file.file_path and os.path.exists(file.file_path):
        try:
            os.remove(file.file_path)
        except Exception as e:
            print(f"Error deleting file {file.file_path}: {e}")
    
    # Delete the database record (cascade will delete operations)
    db.delete(file)
    db.commit()