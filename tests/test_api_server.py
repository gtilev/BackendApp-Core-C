from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import Optional, List, Any
from datetime import date
import os

# Import from app modules
from app.db.session import SessionLocal
from app.core.config import settings
from app.models import AccountingOperation, UploadedFile
from app.services.file_processor import FileProcessor
from app.services.template_detector import TemplateDetector

# Create FastAPI app
app = FastAPI(
    title="Accounting Data Processing API",
    description="API for processing accounting data from Excel files",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create uploads directory
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Accounting Data Processing API", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# FILE ENDPOINTS
@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an Excel file for processing accounting operations."""
    # Validate file extension
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400,
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
            status_code=400,
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

@app.post("/api/files/{file_id}/process")
def process_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Process an uploaded file to extract accounting operations."""
    # Check if file exists
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if file has already been processed
    if file.processed:
        # Get existing operations
        operations = db.query(AccountingOperation).filter(
            AccountingOperation.file_id == file_id
        ).all()
        
        return {"items": operations, "total": len(operations)}
    
    # Process the file
    file_processor = FileProcessor(db)
    operations = file_processor.process_file(file_id)
    
    if not operations:
        raise HTTPException(status_code=500, detail="Failed to process file")
    
    # Get saved operations from database (to ensure we have the IDs)
    db_operations = db.query(AccountingOperation).filter(
        AccountingOperation.file_id == file_id
    ).all()
    
    return {"items": db_operations, "total": len(db_operations)}

@app.get("/api/files/")
def get_files(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    template_type: str = None,
    processed: bool = None
):
    """Retrieve files with filtering and pagination."""
    query = db.query(UploadedFile)
    
    # Apply filters if provided
    if template_type:
        query = query.filter(UploadedFile.template_type == template_type)
    
    if processed is not None:
        query = query.filter(UploadedFile.processed == processed)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    files = query.order_by(UploadedFile.upload_date.desc()).offset(skip).limit(limit).all()
    
    return {"items": files, "total": total}

# OPERATIONS ENDPOINTS
@app.get("/api/operations/")
def get_operations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    document_type: Optional[str] = None,
    debit_account: Optional[str] = None,
    credit_account: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    description_contains: Optional[str] = None,
    template_type: Optional[str] = None,
    file_id: Optional[int] = None,
):
    """Retrieve accounting operations with filtering and pagination."""
    # Start with a base query for all operations
    query = db.query(AccountingOperation).join(
        UploadedFile,
        AccountingOperation.file_id == UploadedFile.id
    )
    
    # Apply filters
    if start_date:
        query = query.filter(AccountingOperation.operation_date >= start_date)
    
    if end_date:
        query = query.filter(AccountingOperation.operation_date <= end_date)
    
    if document_type:
        query = query.filter(AccountingOperation.document_type.ilike(f"%{document_type}%"))
    
    if debit_account:
        query = query.filter(AccountingOperation.debit_account.ilike(f"%{debit_account}%"))
    
    if credit_account:
        query = query.filter(AccountingOperation.credit_account.ilike(f"%{credit_account}%"))
    
    if min_amount is not None:
        query = query.filter(AccountingOperation.amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(AccountingOperation.amount <= max_amount)
    
    if description_contains:
        query = query.filter(AccountingOperation.description.ilike(f"%{description_contains}%"))
    
    if template_type:
        query = query.filter(AccountingOperation.template_type == template_type)
    
    if file_id:
        query = query.filter(AccountingOperation.file_id == file_id)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination and ordering
    operations = query.order_by(AccountingOperation.operation_date.desc()).offset(skip).limit(limit).all()
    
    return {"items": operations, "total": total}

@app.get("/api/operations/{operation_id}")
def get_operation(
    operation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific accounting operation by ID."""
    operation = db.query(AccountingOperation).filter(
        AccountingOperation.id == operation_id
    ).first()
    
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return operation

@app.get("/api/operations/statistics/summary")
def get_operations_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Get summary statistics about accounting operations."""
    # Base query for all operations
    query = db.query(AccountingOperation)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(AccountingOperation.operation_date >= start_date)
    
    if end_date:
        query = query.filter(AccountingOperation.operation_date <= end_date)
    
    # Get total count
    total_operations = query.count()
    
    # Get template counts
    template_counts = db.query(
        AccountingOperation.template_type,
        db.func.count(AccountingOperation.id)
    )
    
    if start_date:
        template_counts = template_counts.filter(AccountingOperation.operation_date >= start_date)
    
    if end_date:
        template_counts = template_counts.filter(AccountingOperation.operation_date <= end_date)
    
    template_counts = template_counts.group_by(
        AccountingOperation.template_type
    ).all()
    
    template_counts_dict = {template: count for template, count in template_counts}
    
    # Get sum of amounts
    total_amount = db.query(
        db.func.sum(AccountingOperation.amount)
    ).select_from(
        AccountingOperation
    )
    
    if start_date:
        total_amount = total_amount.filter(AccountingOperation.operation_date >= start_date)
    
    if end_date:
        total_amount = total_amount.filter(AccountingOperation.operation_date <= end_date)
    
    total_amount = total_amount.scalar() or 0
    
    return {
        "total_operations": total_operations,
        "total_amount": float(total_amount),
        "template_counts": template_counts_dict
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)