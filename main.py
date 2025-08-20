# Main FastAPI application
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

# Import routers and dependencies
from app.api.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.utils.minio_init import init_minio_bucket

# Create the FastAPI application
app = FastAPI(
    title="Accounting API",
    description="""
    API for processing accounting data from various templates.
    
    ## Features
    
    * Excel file upload and processing from various accounting software formats
    * S3-compatible storage using MinIO for scalable file management
    * Automatic template detection and parsing
    
    ## Storage
    
    Files are stored in MinIO S3-compatible object storage for improved scalability and reliability.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "files",
            "description": "Operations with accounting files using S3 storage"
        },
        {
            "name": "auth",
            "description": "Authentication functionality (disabled)"
        },
        {
            "name": "operations",
            "description": "Accounting operations management"
        },
        {
            "name": "system",
            "description": "System-related operations and status"
        }
    ],
    contact={
        "name": "API Support",
        "email": "office@tsvetan.org",
    },
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Accounting Data Processing API", "version": "1.0.0"}

# Health check endpoint
@app.get("/health", tags=["system"])
def health_check():
    health_status = {
        "status": "ok",
        "database": True,
        "s3_storage": None
    }
    
    # Check S3 connection if enabled
    if settings.USE_S3:
        try:
            from app.services.s3 import S3Service
            s3_service = S3Service()
            health_status["s3_storage"] = s3_service.check_connection()
        except Exception:
            health_status["s3_storage"] = False
    
    # Overall status depends on all components
    if settings.USE_S3 and not health_status["s3_storage"]:
        health_status["status"] = "degraded"
    
    return health_status

# Initialize database tables
init_db()

# Initialize MinIO bucket
minio_initialized = init_minio_bucket()
if not minio_initialized and settings.USE_S3:
    print("⚠️ WARNING: MinIO bucket initialization failed. File uploads may not work correctly.")
    print("   Make sure MinIO is running and properly configured in .env file.")
else:
    print("🚀 Application ready to handle file uploads")

# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)