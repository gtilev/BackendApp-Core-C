import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO

from app.services.parsers.base_parser import BaseExcelParser


class AjurParser(BaseExcelParser):
    """Parser for AJUR Excel format"""
    
    def parse(self, file_path: str, file_id: int) -> List[Dict[str, Any]]:
        """
        Parse the AJUR Excel file and extract accounting operations
        
        For AJUR format:
        - вид (Document type)
        - номер (Document number)
        - дата (Date)
        - дебит (Debit account)
        - аналитична (Analytical for debit)
        - кредит (Credit account)
        - аналитична (Analytical for credit)
        - сума (Amount)
        - обяснение (Description)
        
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
                if pd.isna(row.iloc[7]) or (pd.isna(row.iloc[3]) and pd.isna(row.iloc[5])):
                    continue
                
                # Extract and clean data
                operation_date = self.convert_to_date(row.iloc[2])
                document_type = self.clean_string(row.iloc[0])
                document_number = self.clean_string(row.iloc[1])
                debit_account = self.clean_string(row.iloc[3])
                analytical_debit = self.clean_string(row.iloc[4])
                credit_account = self.clean_string(row.iloc[5])
                analytical_credit = self.clean_string(row.iloc[6])
                amount = self.clean_numeric(row.iloc[7])
                description = self.clean_string(row.iloc[8])
                
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
                    "analytical_debit": analytical_debit,
                    "analytical_credit": analytical_credit,
                    "template_type": "ajur",
                    "raw_data": row.to_dict()
                }
                
                operations.append(operation)
            
            return operations
            
        except Exception as e:
            print(f"Error parsing AJUR Excel file: {e}")
            return []
    
    def parse_memory(self, file_obj: BytesIO, file_id: int) -> List[Dict[str, Any]]:
        """
        Parse the AJUR Excel file from memory and extract accounting operations
        
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
                if pd.isna(row.iloc[7]) or (pd.isna(row.iloc[3]) and pd.isna(row.iloc[5])):
                    continue
                
                # Extract and clean data
                operation_date = self.convert_to_date(row.iloc[2])
                document_type = self.clean_string(row.iloc[0])
                document_number = self.clean_string(row.iloc[1])
                debit_account = self.clean_string(row.iloc[3])
                analytical_debit = self.clean_string(row.iloc[4])
                credit_account = self.clean_string(row.iloc[5])
                analytical_credit = self.clean_string(row.iloc[6])
                amount = self.clean_numeric(row.iloc[7])
                description = self.clean_string(row.iloc[8])
                
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
                    "analytical_debit": analytical_debit,
                    "analytical_credit": analytical_credit,
                    "template_type": "ajur",
                    "raw_data": row.to_dict()
                }
                
                operations.append(operation)
            
            return operations
            
        except Exception as e:
            print(f"Error parsing AJUR Excel file from memory: {e}")
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
            header_keywords = ["вид", "номер", "дата", "дебит", "кредит", "аналитична", "сума", "обяснение"]
            matches = sum(any(keyword in val for keyword in header_keywords) for val in row_values)
            
            if matches >= 4:  # If we find at least 4 header keywords
                return i + 1  # Data starts in the next row
        
        return 0  # If no header found, assume data starts at row 0