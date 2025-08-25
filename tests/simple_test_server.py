from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(
    title="Accounting API Test Server",
    description="Simple test server for API testing",
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

# Root endpoint
@app.get("/")
def root():
    return {"message": "Accounting Data Processing API", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Mock data
mock_files = [
    {"id": 1, "filename": "example1.xls", "template_type": "rival", "processed": True},
    {"id": 2, "filename": "example2.xls", "template_type": "ajur", "processed": False}
]

mock_operations = [
    {
        "id": 1,
        "file_id": 1,
        "operation_date": "2025-01-15",
        "document_type": "invoice",
        "debit_account": "411",
        "credit_account": "701",
        "amount": 1000.50,
        "description": "Sale of goods",
        "template_type": "rival"
    },
    {
        "id": 2,
        "file_id": 1,
        "operation_date": "2025-01-20",
        "document_type": "receipt",
        "debit_account": "501",
        "credit_account": "401",
        "amount": 500.25,
        "description": "Purchase of supplies",
        "template_type": "rival"
    }
]

# FILE ENDPOINTS
@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Mock endpoint for file upload."""
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only Excel files (.xls, .xlsx) are supported."
        )
    
    # Return mock file data
    return {
        "id": len(mock_files) + 1,
        "filename": file.filename,
        "template_type": "rival",
        "processed": False,
        "upload_date": "2025-08-20T00:00:00Z",
        "file_path": f"/uploads/{file.filename}"
    }

@app.post("/api/files/{file_id}/process")
def process_file(file_id: int):
    """Mock endpoint for file processing."""
    if file_id > len(mock_files):
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "items": [op for op in mock_operations if op["file_id"] == file_id],
        "total": len([op for op in mock_operations if op["file_id"] == file_id])
    }

@app.get("/api/files/")
def get_files(skip: int = 0, limit: int = 100):
    """Mock endpoint for listing files."""
    return {
        "items": mock_files[skip:skip+limit],
        "total": len(mock_files)
    }

@app.get("/api/files/{file_id}")
def get_file(file_id: int):
    """Mock endpoint for file details."""
    if file_id > len(mock_files):
        raise HTTPException(status_code=404, detail="File not found")
    
    file = mock_files[file_id - 1]
    return {
        **file,
        "operation_count": len([op for op in mock_operations if op["file_id"] == file_id])
    }

# OPERATIONS ENDPOINTS
@app.get("/api/operations/")
def get_operations(skip: int = 0, limit: int = 100):
    """Mock endpoint for listing operations."""
    return {
        "items": mock_operations[skip:skip+limit],
        "total": len(mock_operations)
    }

@app.get("/api/operations/{operation_id}")
def get_operation(operation_id: int):
    """Mock endpoint for operation details."""
    if operation_id > len(mock_operations):
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return mock_operations[operation_id - 1]

@app.get("/api/operations/statistics/summary")
def get_operations_summary():
    """Mock endpoint for operation statistics."""
    template_counts = {}
    for op in mock_operations:
        template_type = op["template_type"]
        if template_type in template_counts:
            template_counts[template_type] += 1
        else:
            template_counts[template_type] = 1
    
    total_amount = sum(op["amount"] for op in mock_operations)
    
    return {
        "total_operations": len(mock_operations),
        "total_amount": float(total_amount),
        "template_counts": template_counts
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)