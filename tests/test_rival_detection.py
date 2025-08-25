import sys
import os
from app.services.template_detector import TemplateDetector

# Setup paths
file_path = "files/хронология Ривал.xls"

# Make sure the file exists
if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    sys.exit(1)

# Create detector and run detection
print(f"Testing template detection for file: {file_path}")
detector = TemplateDetector()
template_type = detector.detect_template(file_path)

# Display result
print("\n" + "="*50)
print(f"Detection result: {template_type}")
print("="*50)

if template_type:
    print(f"SUCCESS: Detected template type: {template_type.value}")
    sys.exit(0)
else:
    print("FAILURE: Could not detect template type.")
    sys.exit(1)