import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO

from app.services.parsers.base_parser import BaseExcelParser


class RivalParser(BaseExcelParser):
    """Parser for Rival Excel format"""
    
    def parse(self, file_path: str, file_id: int) -> List[Dict[str, Any]]:
        """
        Parse the Rival Excel file and extract accounting operations
        
        For Rival format:
        - Column 1: Вид документ (Document type)
        - Column 2: Номер на документ (Document number)
        - Column 3: Дата (Date)
        - Column 4: Име (Name/Partner)
        - Column 5: Дебит (Debit account)
        - Column 6: Кредит (Credit account)
        - Column 7: Сума (Amount)
        - Column 8: Обяснение (Description)
        
        Args:
            file_path: Path to the Excel file
            file_id: ID of the uploaded file in the database
            
        Returns:
            List of dictionaries containing accounting operations data
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Skip header rows if necessary
            # Detect the start of actual data
            data_start_row = self._find_data_start_row(df)
            if data_start_row > 0:
                df = df.iloc[data_start_row:]
                df = df.reset_index(drop=True)
            
            operations = []
            
            # Process each row
            for _, row in df.iterrows():
                # Skip rows that don't have amount or both debit and credit accounts
                if pd.isna(row.iloc[6]) or (pd.isna(row.iloc[4]) and pd.isna(row.iloc[5])):
                    continue
                
                # Extract and clean data
                operation_date = self.convert_to_date(row.iloc[2])
                document_type = self.clean_string(row.iloc[0])
                document_number = self.clean_string(row.iloc[1])
                partner_name = self.clean_string(row.iloc[3])
                debit_account = self.clean_string(row.iloc[4])
                credit_account = self.clean_string(row.iloc[5])
                amount = self.clean_numeric(row.iloc[6])
                description = self.clean_string(row.iloc[7])
                
                # Skip if we don't have a valid date or amount
                if not operation_date or not amount:
                    continue
                
                # Create operation dictionary
                operation = {
                    "file_id": file_id,
                    "operation_date": operation_date,
                    "document_type": document_type,
                    "document_number": document_number,
                    "debit_account": debit_account,
                    "credit_account": credit_account,
                    "amount": amount,
                    "description": description,
                    "partner_name": partner_name,
                    "template_type": "rival",
                    "raw_data": row.to_dict()
                }
                
                operations.append(operation)
            
            return operations
            
        except Exception as e:
            print(f"Error parsing Rival Excel file: {e}")
            return []
    
    def parse_memory(self, file_obj: BytesIO, file_id: int) -> List[Dict[str, Any]]:
        """
        Parse the Rival Excel file from memory and extract accounting operations
        
        Args:
            file_obj: BytesIO object containing the Excel file
            file_id: ID of the uploaded file in the database
            
        Returns:
            List of dictionaries containing accounting operations data
        """
        try:
            # Reset file pointer to beginning
            file_obj.seek(0)
            
            # Read Excel file from memory
            df = pd.read_excel(file_obj)
            
            # Skip header rows if necessary
            # Detect the start of actual data
            data_start_row = self._find_data_start_row(df)
            if data_start_row > 0:
                df = df.iloc[data_start_row:]
                df = df.reset_index(drop=True)
            
            operations = []
            
            # Process each row
            for _, row in df.iterrows():
                # Skip rows that don't have amount or both debit and credit accounts
                if pd.isna(row.iloc[6]) or (pd.isna(row.iloc[4]) and pd.isna(row.iloc[5])):
                    continue
                
                # Extract and clean data
                operation_date = self.convert_to_date(row.iloc[2])
                document_type = self.clean_string(row.iloc[0])
                document_number = self.clean_string(row.iloc[1])
                partner_name = self.clean_string(row.iloc[3])
                debit_account = self.clean_string(row.iloc[4])
                credit_account = self.clean_string(row.iloc[5])
                amount = self.clean_numeric(row.iloc[6])
                description = self.clean_string(row.iloc[7])
                
                # Skip if we don't have a valid date or amount
                if not operation_date or not amount:
                    continue
                
                # Create operation dictionary
                operation = {
                    "file_id": file_id,
                    "operation_date": operation_date,
                    "document_type": document_type,
                    "document_number": document_number,
                    "debit_account": debit_account,
                    "credit_account": credit_account,
                    "amount": amount,
                    "description": description,
                    "partner_name": partner_name,
                    "template_type": "rival",
                    "raw_data": row.to_dict()
                }
                
                operations.append(operation)
            
            return operations
            
        except Exception as e:
            print(f"Error parsing Rival Excel file from memory: {e}")
            return []
    
    def _find_data_start_row(self, df: pd.DataFrame) -> int:
        """
        Find the row where actual data starts
        
        Args:
            df: DataFrame with the Excel content
            
        Returns:
            Row index where data starts (0-based)
        """
        # Look for rows that contain typical header values
        for i in range(min(10, len(df))):
            row_values = [str(val).lower() for val in df.iloc[i].values if not pd.isna(val)]
            
            # Check if the row contains keywords that suggest it's a header
            header_keywords = ["вид", "документ", "номер", "дата", "дебит", "кредит", "сума", "обяснение"]
            matches = sum(any(keyword in val for keyword in header_keywords) for val in row_values)
            
            if matches >= 4:  # If we find at least 4 header keywords
                return i + 1  # Data starts in the next row
        
        return 0  # If no header found, assume data starts at row 0