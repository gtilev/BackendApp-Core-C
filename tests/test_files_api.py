import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.services.template_detector import TemplateType
from app.services.file_processor import FileProcessor


def test_upload_file_invalid_format(client, user_token_headers):
    """Test uploading a file with an invalid format"""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"This is not an Excel file")
        temp_file.seek(0)
        
        # Upload the file
        response = client.post(
            "/api/files/upload",
            headers=user_token_headers,
            files={"file": ("test.txt", temp_file, "text/plain")}
        )
        
        # Check the response
        assert response.status_code == 400
        assert "Invalid file format" in response.json()["detail"]


@patch.object(TemplateType, "RIVAL", "rival")
@patch("app.services.template_detector.TemplateDetector.detect_template")
def test_upload_file_success(mock_detect_template, client, user_token_headers, db):
    """Test successful file upload"""
    # Mock the template detection
    mock_detect_template.return_value = TemplateType.RIVAL
    
    # Create a temporary Excel-like file
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
        temp_file.write(b"Mock Excel content")
        temp_file.seek(0)
        
        # Upload the file
        response = client.post(
            "/api/files/upload",
            headers=user_token_headers,
            files={"file": ("test.xlsx", temp_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        # Check the response
        assert response.status_code == 200
        assert response.json()["filename"] == "test.xlsx"
        assert response.json()["template_type"] == "rival"
        assert response.json()["processed"] is False
        
        # Verify the file was added to the database
        file_id = response.json()["id"]
        assert file_id is not None


@patch.object(FileProcessor, "process_file")
def test_process_file(mock_process_file, client, user_token_headers, db, test_user):
    """Test processing a file"""
    # Add a test file to the database
    from app.models.file import UploadedFile
    test_file = UploadedFile(
        filename="test.xlsx",
        template_type="rival",
        file_path="test_path.xlsx",
        user_id=test_user.id,
        processed=False
    )
    db.add(test_file)
    db.commit()
    
    # Mock the file processing to return some operations
    mock_process_file.return_value = [
        {
            "operation_date": "2023-01-01",
            "document_type": "Test Doc",
            "amount": 100.0,
            "debit_account": "101",
            "credit_account": "201",
            "description": "Test operation"
        }
    ]
    
    # Process the file
    response = client.post(
        f"/api/files/{test_file.id}/process",
        headers=user_token_headers
    )
    
    # Check the response
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    
    # Verify the process_file method was called
    mock_process_file.assert_called_once_with(test_file.id)


def test_get_files(client, user_token_headers, db, test_user):
    """Test getting a list of files"""
    # Add test files to the database
    from app.models.file import UploadedFile
    test_file1 = UploadedFile(
        filename="test1.xlsx",
        template_type="rival",
        file_path="test_path1.xlsx",
        user_id=test_user.id,
        processed=False
    )
    test_file2 = UploadedFile(
        filename="test2.xlsx",
        template_type="ajur",
        file_path="test_path2.xlsx",
        user_id=test_user.id,
        processed=True
    )
    db.add(test_file1)
    db.add(test_file2)
    db.commit()
    
    # Get the files
    response = client.get(
        "/api/files/",
        headers=user_token_headers
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 2
    
    # Test filtering by template type
    response = client.get(
        "/api/files/?template_type=rival",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["template_type"] == "rival"