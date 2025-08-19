from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime


class BaseExcelParser(ABC):
    """Base class for all Excel parsers"""
    
    @abstractmethod
    def parse(self, file_path: str, file_id: int) -> List[Dict[str, Any]]:
        """
        Parse the Excel file and extract accounting operations
        
        Args:
            file_path: Path to the Excel file
            file_id: ID of the uploaded file in the database
            
        Returns:
            List of dictionaries containing accounting operations data
        """
        pass
    
    def clean_column_name(self, name: str) -> str:
        """
        Clean column name for consistent processing
        
        Args:
            name: Raw column name
            
        Returns:
            Cleaned column name (lowercase, trimmed)
        """
        return str(name).lower().strip()
    
    def convert_to_date(self, date_value: Any) -> Optional[datetime.date]:
        """
        Convert various date formats to standard date
        
        Args:
            date_value: Date value in various formats (string, datetime, etc.)
            
        Returns:
            Standardized date object or None if conversion fails
        """
        if pd.isna(date_value):
            return None
            
        try:
            if isinstance(date_value, datetime):
                return date_value.date()
            elif isinstance(date_value, str):
                # Try different date formats
                for fmt in ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                    try:
                        return datetime.strptime(date_value, fmt).date()
                    except ValueError:
                        continue
                
                # If none of the formats match, try pandas to_datetime
                return pd.to_datetime(date_value).date()
            else:
                # Try using pandas to convert numeric or other types
                return pd.to_datetime(date_value).date()
        except Exception as e:
            print(f"Error converting date {date_value}: {e}")
            return None
    
    def clean_numeric(self, value: Any) -> Optional[float]:
        """
        Clean and convert numeric values
        
        Args:
            value: Value to convert to float
            
        Returns:
            Cleaned float value or None if conversion fails
        """
        if pd.isna(value):
            return None
            
        try:
            if isinstance(value, str):
                # Remove currency symbols and thousand separators
                cleaned = value.replace('$', '').replace('€', '').replace(' ', '')
                cleaned = cleaned.replace(',', '.').replace(' ', '')
                return float(cleaned)
            else:
                return float(value)
        except Exception as e:
            print(f"Error converting numeric value {value}: {e}")
            return None
    
    def clean_string(self, value: Any) -> Optional[str]:
        """
        Clean string values
        
        Args:
            value: Value to convert to string
            
        Returns:
            Cleaned string value or None if empty or NaN
        """
        if pd.isna(value):
            return None
            
        try:
            result = str(value).strip()
            return result if result else None
        except Exception as e:
            print(f"Error converting string value {value}: {e}")
            return None