# MinIO Setup for File Storage

This project uses MinIO as an S3-compatible object storage service for handling file uploads. Below are instructions for setting up and working with MinIO.

## Overview

MinIO is a high-performance, S3-compatible object storage system. It's used in this application to store uploaded Excel files instead of using the local file system. This provides several benefits:

- Scalable storage that can grow as needed
- Consistency across multiple application instances
- Compatibility with the AWS S3 API
- Better resilience and data durability

## Development Setup

For development, a single-node MinIO instance is automatically set up with Docker Compose:

```bash
# Start the application with MinIO
docker-compose up -d
```

The MinIO server will be available at:
- S3 API Endpoint: http://localhost:9000
- MinIO Console: http://localhost:9001

Default credentials (from .env file):
- Username: minioadmin
- Password: minioadminStrongPass

## Production Setup

For production environments, the MinIO service is configured in `docker-compose.prod.yml`. In production, you should consider:

1. Using a distributed MinIO setup for better reliability
2. Setting stronger credentials in .env.prod
3. Implementing proper backup strategies

```bash
# Start the production environment
docker-compose -f docker-compose.prod.yml up -d
```

## Manual Testing with MinIO Client (mc)

You can use the MinIO Client (mc) to interact with your MinIO instance:

```bash
# Install mc (MinIO Client)
# For Linux: 
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# For Windows:
# Download from https://dl.min.io/client/mc/release/windows-amd64/mc.exe

# Configure mc with your MinIO instance
mc alias set local http://localhost:9000 minioadmin minioadminStrongPass

# Create a bucket (if not already created by the application)
mc mb local/accounting-files

# List buckets
mc ls local

# Upload a file for testing
mc cp ./your-file.xlsx local/accounting-files/

# List files in the bucket
mc ls local/accounting-files
```

## Configuration

The S3 connection is configured through environment variables in the `.env` file:

```
USE_S3=true
S3_BUCKET=accounting-files
S3_REGION=us-east-1
AWS_ACCESS_KEY=minioadmin
AWS_SECRET_KEY=minioadminStrongPass
S3_ENDPOINT_URL=http://localhost:9000
```

For docker environments, the S3_ENDPOINT_URL is automatically set to `http://minio:9000` to use the Docker service name.

## Troubleshooting

If you encounter issues with MinIO:

1. Check that MinIO service is running: `docker-compose ps`
2. Verify credentials in .env file match the MinIO service configuration
3. Ensure the bucket exists: `mc ls local`
4. Check application logs for specific S3 errors

For more detailed MinIO documentation, visit [min.io/docs](https://min.io/docs).