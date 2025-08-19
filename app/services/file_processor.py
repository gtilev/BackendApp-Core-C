import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.file import UploadedFile
from app.models.operation import AccountingOperation
from app.services.template_detector import TemplateDetector, TemplateType
from app.services.parsers.rival_parser import RivalParser
from app.services.parsers.ajur_parser import AjurParser
# Import other parsers as they are implemented
# from app.services.parsers.microinvest_parser import MicroinvestParser
# from app.services.parsers.business_navigator_parser import BusinessNavigatorParser
# from app.services.parsers.universum_parser import UniversumParser


class FileProcessor:
    """Service for processing uploaded Excel files"""
    
    def __init__(self, db: Session):
        self.db = db
        self.template_detector = TemplateDetector()
        
        # Initialize parsers
        self.parsers = {
            TemplateType.RIVAL: RivalParser(),
            TemplateType.AJUR: AjurParser(),
            # Add other parsers as they are implemented
            # TemplateType.MICROINVEST: MicroinvestParser(),
            # TemplateType.BUSINESS_NAVIGATOR: BusinessNavigatorParser(),
            # TemplateType.UNIVERSUM: UniversumParser(),
        }
    
    def create_file(self, filename: str, template_type: str, file_path: str) -> UploadedFile:
        """
        Create a record for an uploaded file
        
        Args:
            filename: Original filename
            template_type: Detected template type
            file_path: Path where the file is stored
            
        Returns:
            Created UploadedFile record
        """
        db_file = UploadedFile(
            filename=filename,
            template_type=template_type,
            file_path=file_path,
            processed=False
        )
        
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file
    
    def process_file(self, file_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Process a file that has been uploaded
        
        Args:
            file_id: ID of the file to process
            
        Returns:
            List of processed operations or None if processing failed
        """
        # Get file record
        file_record = self.db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not file_record:
            print(f"File with ID {file_id} not found")
            return None
        
        # Check if file exists
        if not os.path.exists(file_record.file_path):
            print(f"File {file_record.file_path} does not exist")
            return None
        
        try:
            # Get parser for the template type
            parser = self.parsers.get(file_record.template_type)
            if not parser:
                print(f"No parser available for template type {file_record.template_type}")
                return None
            
            # Parse the file
            operations = parser.parse(file_record.file_path, file_id)
            
            # Save operations to database
            for operation_data in operations:
                operation = AccountingOperation(**operation_data)
                self.db.add(operation)
            
            # Mark file as processed
            file_record.processed = True
            
            # Commit changes
            self.db.commit()
            
            return operations
            
        except Exception as e:
            self.db.rollback()
            print(f"Error processing file {file_id}: {e}")
            return None
    
    def detect_template(self, file_path: str) -> Optional[str]:
        """
        Detect the template type of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Template type as string or None if detection failed
        """
        template_type = self.template_detector.detect_template(file_path)
        return template_type.value if template_type else None