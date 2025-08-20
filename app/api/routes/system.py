from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.s3 import S3Service

router = APIRouter(tags=["system"])


@router.get("/s3-status", summary="Check S3 storage status",
           description="Verify connection to S3 storage and bucket existence")
def check_s3_status() -> Dict[str, Any]:
    """
    Check the status of the S3 storage connection and bucket
    """
    if not settings.USE_S3:
        return {
            "enabled": False,
            "message": "S3 storage is not enabled in configuration"
        }
    
    try:
        s3_service = S3Service()
        
        # Check connection
        connection_ok = s3_service.check_connection()
        if not connection_ok:
            return {
                "enabled": True,
                "connection": False,
                "message": "Cannot connect to S3 endpoint"
            }
        
        # Check if our bucket exists
        s3_client = s3_service._get_s3_client()
        try:
            s3_client.head_bucket(Bucket=settings.S3_BUCKET)
            bucket_exists = True
        except Exception:
            bucket_exists = False
        
        return {
            "enabled": True,
            "connection": True,
            "bucket_exists": bucket_exists,
            "bucket_name": settings.S3_BUCKET,
            "endpoint": settings.S3_ENDPOINT_URL or "AWS S3"
        }
        
    except Exception as e:
        return {
            "enabled": True,
            "connection": False,
            "error": str(e),
            "message": "Error checking S3 status"
        }


@router.post("/test-s3-upload", summary="Test S3 upload functionality",
            description="Upload a test file to S3 to verify functionality")
async def test_s3_upload(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Test uploading a file to S3 storage
    """
    if not settings.USE_S3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="S3 storage is not enabled in configuration"
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        # Create test object name
        test_object_name = f"test-upload/{file.filename}"
        
        # Upload to S3
        s3_service = S3Service()
        success, message = s3_service.upload_file(contents, test_object_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload test file: {message}"
            )
        
        return {
            "success": True,
            "file": file.filename,
            "object_key": test_object_name,
            "bucket": settings.S3_BUCKET,
            "message": "Test file uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during test upload: {str(e)}"
        )