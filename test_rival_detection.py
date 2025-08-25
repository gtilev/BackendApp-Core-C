import sys
from app.services.template_detector import TemplateDetector, TemplateType
from fastapi.testclient import TestClient
from app.app import app
import os

# Create a test client
client = TestClient(app)

def test_template_detector_directly():
    """Test the template detector directly with the Rival file"""
    rival_file_path = "files/хронология Ривал.xls"
    
    # Make sure the file exists
    if not os.path.exists(rival_file_path):
        print(f"ERROR: File not found at {rival_file_path}")
        return False
    
    print(f"\nTesting template detection directly for file: {rival_file_path}")
    detector = TemplateDetector()
    template_type = detector.detect_template(rival_file_path)
    
    print("\n" + "="*50)
    print(f"Direct detection result: {template_type}")
    print("="*50)
    
    if template_type == TemplateType.RIVAL:
        print("SUCCESS: Correctly detected as Rival template")
        return True
    else:
        print(f"FAILURE: Detected as {template_type} instead of Rival")
        return False

def test_upload_api():
    """Test the file upload API with the Rival file"""
    rival_file_path = "files/хронология Ривал.xls"
    
    # Make sure the file exists
    if not os.path.exists(rival_file_path):
        print(f"ERROR: File not found at {rival_file_path}")
        return False
    
    print(f"\nTesting file upload API with file: {rival_file_path}")
    
    # Open the file and prepare for upload
    with open(rival_file_path, "rb") as f:
        files = {"file": (os.path.basename(rival_file_path), f, "application/vnd.ms-excel")}
        
        # Make the API request
        response = client.post("/api/files/upload", files=files)
    
    print("\n" + "="*50)
    print(f"API response status code: {response.status_code}")
    print(f"API response: {response.json() if response.status_code == 200 else response.text}")
    print("="*50)
    
    if response.status_code == 200 and response.json().get("template_type") == "rival":
        print("SUCCESS: API correctly detected file as Rival template")
        return True
    else:
        print("FAILURE: API failed to detect file as Rival template")
        return False

if __name__ == "__main__":
    print("="*50)
    print("TESTING RIVAL TEMPLATE DETECTION")
    print("="*50)
    
    # Test direct detector
    direct_result = test_template_detector_directly()
    
    # Test API
    api_result = test_upload_api()
    
    # Final result
    print("\n" + "="*50)
    if direct_result and api_result:
        print("ALL TESTS PASSED! Rival template detection is working correctly.")
        sys.exit(0)
    elif direct_result:
        print("PARTIAL SUCCESS: Direct detection works but API upload failed")
        sys.exit(1)
    else:
        print("TESTS FAILED: Rival template detection is not working correctly")
        sys.exit(1)