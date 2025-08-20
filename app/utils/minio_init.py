import logging
from botocore.exceptions import ClientError

from app.core.config import settings
from app.services.s3 import S3Service

logger = logging.getLogger(__name__)

def init_minio_bucket():
    """
    Initialize the MinIO bucket if it doesn't exist.
    This should be called when the application starts.
    """
    if not settings.USE_S3:
        logger.info("S3 storage is disabled, skipping MinIO bucket initialization")
        return
    
    try:
        s3_service = S3Service()
        s3_client = s3_service._get_s3_client()
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=settings.S3_BUCKET)
            logger.info(f"MinIO bucket '{settings.S3_BUCKET}' already exists")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            # If bucket doesn't exist (404) or we don't have access to check (403)
            if error_code in ['404', '403']:
                # Create the bucket
                logger.info(f"Creating MinIO bucket: {settings.S3_BUCKET}")
                s3_client.create_bucket(Bucket=settings.S3_BUCKET)
                logger.info(f"MinIO bucket '{settings.S3_BUCKET}' created successfully")
            else:
                # Re-raise other errors
                raise
    
    except Exception as e:
        logger.error(f"Error initializing MinIO bucket: {e}")