import io
import logging
from typing import Optional, BinaryIO, Union, Tuple

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    """Service for interacting with AWS S3 or S3-compatible storage"""
    
    def __init__(self):
        """Initialize S3 client using application settings"""
        self.s3_client = self._get_s3_client()
        self.bucket_name = settings.S3_BUCKET
    
    def _get_s3_client(self):
        """
        Create and return a boto3 S3 client
        
        If S3_ENDPOINT_URL is set, it will be used for S3-compatible services like MinIO
        """
        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        
        # Use endpoint URL for MinIO or other S3-compatible services if provided
        return session.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            # For MinIO and testing, we might want to disable verification
            verify=settings.S3_ENDPOINT_URL is None
        )
    
    def check_connection(self) -> bool:
        """
        Check if the connection to S3/MinIO is working
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # List buckets to check if connection works
            self.s3_client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"S3 connection check failed: {e}")
            return False
    
    def upload_file(self, file_content: Union[BinaryIO, bytes], object_name: str) -> Tuple[bool, str]:
        """
        Upload a file to S3
        
        Args:
            file_content: Content to upload (file-like object or bytes)
            object_name: S3 object name (key)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # If file_content is bytes, convert to file-like object
            if isinstance(file_content, bytes):
                file_content = io.BytesIO(file_content)
                
            self.s3_client.upload_fileobj(file_content, self.bucket_name, object_name)
            return True, f"File {object_name} uploaded successfully"
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return False, f"Error uploading file: {str(e)}"
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        """
        Download a file from S3
        
        Args:
            object_name: S3 object name (key)
            
        Returns:
            File content as bytes or None if error
        """
        try:
            # Use BytesIO to store the file content
            file_obj = io.BytesIO()
            
            # Download the file to the BytesIO object
            self.s3_client.download_fileobj(self.bucket_name, object_name, file_obj)
            
            # Reset the file position to the beginning and return the content
            file_obj.seek(0)
            return file_obj.read()
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            return None
    
    def delete_file(self, object_name: str) -> Tuple[bool, str]:
        """
        Delete a file from S3
        
        Args:
            object_name: S3 object name (key)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True, f"File {object_name} deleted successfully"
        except ClientError as e:
            logger.error(f"Error deleting from S3: {e}")
            return False, f"Error deleting file: {str(e)}"
    
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for an S3 object
        
        Args:
            object_name: S3 object name (key)
            expiration: Time in seconds for the URL to remain valid
            
        Returns:
            Presigned URL as string or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None