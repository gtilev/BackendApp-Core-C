import logging
import time
from botocore.exceptions import ClientError, EndpointConnectionError

from app.core.config import settings
from app.services.s3 import S3Service

logger = logging.getLogger(__name__)
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

def init_minio_bucket():
    """
    Initialize the MinIO bucket if it doesn't exist.
    This should be called when the application starts.
    """
    if not settings.USE_S3:
        logger.info("S3 storage is disabled, skipping MinIO bucket initialization")
        return
    
    # Try with retries to handle case where MinIO might not be ready yet
    retries = 0
    while retries < MAX_RETRIES:
        try:
            s3_service = S3Service()
            s3_client = s3_service._get_s3_client()
            
            # Check if bucket exists
            try:
                s3_client.head_bucket(Bucket=settings.S3_BUCKET)
                logger.info(f"MinIO bucket '{settings.S3_BUCKET}' already exists")
                print(f"✅ MinIO bucket '{settings.S3_BUCKET}' verified and ready to use")
                return True
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                # If bucket doesn't exist (404) or we don't have access to check (403)
                if error_code in ['404', '403']:
                    # Create the bucket
                    logger.info(f"Creating MinIO bucket: {settings.S3_BUCKET}")
                    s3_client.create_bucket(Bucket=settings.S3_BUCKET)
                    logger.info(f"MinIO bucket '{settings.S3_BUCKET}' created successfully")
                    print(f"✅ MinIO bucket '{settings.S3_BUCKET}' created successfully")
                    
                    # Verify the bucket was created
                    s3_client.head_bucket(Bucket=settings.S3_BUCKET)
                    return True
                else:
                    # Re-raise other errors
                    raise
        
        except EndpointConnectionError as e:
            retries += 1
            if retries < MAX_RETRIES:
                logger.warning(f"MinIO service not ready yet. Retrying in {RETRY_DELAY} seconds... (Attempt {retries}/{MAX_RETRIES})")
                print(f"⏳ Waiting for MinIO service to be ready... (Attempt {retries}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Failed to connect to MinIO after several attempts")
                print("❌ Failed to connect to MinIO after several attempts")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing MinIO bucket: {e}")
            print(f"❌ Error initializing MinIO bucket: {e}")
            return False
    
    return False