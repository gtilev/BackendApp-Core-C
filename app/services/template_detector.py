from enum import Enum
from typing import Optional, IO, List, Union
import pandas as pd
from io import BytesIO


class TemplateType(str, Enum):
    RIVAL = "rival"
    AJUR = "ajur"
    MICROINVEST = "microinvest"
    BUSINESS_NAVIGATOR = "business_navigator"
    UNIVERSUM = "universum"


class TemplateDetector:
    """Service for detecting the template type of an Excel file"""

    def detect_template(self, file_path: str) -> Optional[TemplateType]:
        """
        Detect the template type based on file content and structure
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            TemplateType or None if the template cannot be detected
        """
        try:
            # Read first few rows to analyze headers
            df = pd.read_excel(file_path, nrows=10)
            return self._analyze_dataframe(df)
        except Exception as e:
            # Log the error
            print(f"Error detecting template: {e}")
            return None
    
    def detect_template_from_bytes(self, file_obj: Union[BytesIO, bytes]) -> Optional[TemplateType]:
        """
        Detect the template type from file content in memory
        
        Args:
            file_obj: BytesIO object or bytes containing the Excel file
            
        Returns:
            TemplateType or None if the template cannot be detected
        """
        try:
            print("[DEBUG] Starting detect_template_from_bytes")
            
            # If we received bytes, convert to BytesIO
            if isinstance(file_obj, bytes):
                file_obj = BytesIO(file_obj)
                print("[DEBUG] Converted bytes to BytesIO")
                
            # Reset file pointer to beginning just in case
            file_obj.seek(0)
            
            # Read first few rows to analyze headers
            print("[DEBUG] Reading Excel file with pandas")
            df = pd.read_excel(file_obj, nrows=10)
            print(f"[DEBUG] DataFrame shape: {df.shape}")
            
            # Print headers as a list
            headers = [str(col) for col in df.columns]
            print(f"[DEBUG] Excel headers: {headers}")
            
            # Print first few rows for debugging
            print("[DEBUG] First 3 rows of data:")
            print(df.head(3))
            
            return self._analyze_dataframe(df)
        except Exception as e:
            # Log the error
            print(f"[ERROR] Error detecting template from bytes: {e}")
            return None
    
    def _analyze_dataframe(self, df: pd.DataFrame) -> Optional[TemplateType]:
        """
        Analyze a DataFrame to determine the template type
        
        Args:
            df: Pandas DataFrame containing the Excel data
            
        Returns:
            TemplateType or None if the template cannot be detected
        """
        print("[DEBUG] Starting _analyze_dataframe")
        
        # Convert headers to lowercase strings for easier comparison
        headers = self._get_headers(df)
        print(f"[DEBUG] Lowercase headers: {headers}")
        
        # Check for each template type
        print("[DEBUG] Checking Rival pattern")
        if self._check_rival_pattern(df, headers):
            print("[DEBUG] Matched Rival pattern")
            return TemplateType.RIVAL
        
        print("[DEBUG] Checking Ajur pattern")
        if self._check_ajur_pattern(df, headers):
            print("[DEBUG] Matched Ajur pattern")
            return TemplateType.AJUR
        
        print("[DEBUG] Checking Microinvest pattern")
        if self._check_microinvest_pattern(df, headers):
            print("[DEBUG] Matched Microinvest pattern")
            return TemplateType.MICROINVEST
        
        print("[DEBUG] Checking Business Navigator pattern")
        if self._check_business_navigator_pattern(df, headers):
            print("[DEBUG] Matched Business Navigator pattern")
            return TemplateType.BUSINESS_NAVIGATOR
        
        print("[DEBUG] Checking Universum pattern")
        if self._check_universum_pattern(df, headers):
            print("[DEBUG] Matched Universum pattern")
            return TemplateType.UNIVERSUM
        
        print("[DEBUG] No template pattern matched")
        return None
    
    def _get_headers(self, df: pd.DataFrame) -> List[str]:
        """Convert DataFrame headers to lowercase strings"""
        return [str(col).lower() for col in df.columns]
    
    def _check_rival_pattern(self, df: pd.DataFrame, headers: List[str]) -> bool:
        """
        Check if the file matches the Rival template pattern
        
        Rival: колона 1 вид документ, колона 2 номер на документ, дата, име, дебит, кредит, сума, обяснение
        """
        # Check for specific column patterns in Rival template
        expected_keywords = ["вид документ", "номер на документ", "дата", "дебит", "кредит", "сума", "обяснение"]
        return any("вид документ" in h for h in headers) and any("номер" in h for h in headers) and \
               self._check_keywords_in_headers(headers, expected_keywords, min_matches=4)
    
    def _check_ajur_pattern(self, df: pd.DataFrame, headers: List[str]) -> bool:
        """
        Check if the file matches the AJUR template pattern
        
        AJUR: вид, номер, дата, дебит, аналитична, кредит, аналитична, сума, обяснение
        """
        print("[DEBUG] Inside _check_ajur_pattern")
        
        # Update expected keywords to match the actual headers (case-insensitive)
        expected_keywords = ["№",
                             "дата рег",
                             "вид док",
                             "документ no / дата",
                             "рег. no",
                             "дт с/ка",
                             "аналитична сметка",
                             "кт с/ка",
                             "количество",
                             "мярка",
                             "сума",
                             "обяснителен текст",
                             "установено при одита",
                             "отклонение",
                             "тествани на контролни действия",
                             "установено наличие  на контролно действие   при одита",
                             ]
        
        print(f"[DEBUG] Expected Ajur keywords: {expected_keywords}")
        
        # Check for the specific pattern
        # Make the check case-insensitive by comparing lowercase versions
        has_vid_dok = any("вид док" in h.lower() for h in headers)
        print(f"[DEBUG] Has 'вид док' in headers (case-insensitive): {has_vid_dok}")
        
        # Check for keyword matches
        keyword_matches = self._check_keywords_in_headers(headers, expected_keywords, min_matches=16)
        print(f"[DEBUG] Ajur keyword matches result: {keyword_matches}")
        
        result = has_vid_dok and keyword_matches
        print(f"[DEBUG] Ajur pattern match result: {result}")
        
        return result
    
    def _check_microinvest_pattern(self, df: pd.DataFrame, headers: List[str]) -> bool:
        """
        Check if the file matches the Microinvest template pattern
        
        Микроинвест: дебит с-ка, кредит с-ка, вид документ, дата, номер на док, партньор, основание
        """
        # Check for specific column patterns in Microinvest template
        expected_keywords = ["дебит", "кредит", "с-ка", "вид документ", "дата", "номер", "партньор", "основание"]
        return any("партньор" in h for h in headers) and \
               self._check_keywords_in_headers(headers, expected_keywords, min_matches=5)
    
    def _check_business_navigator_pattern(self, df: pd.DataFrame, headers: List[str]) -> bool:
        """
        Check if the file matches the Business Navigator template pattern
        
        Бизнес навигатор: док тип, док номер, док дата, счетоводен текст, сума дебит, номер на сметка, име на сметка, сметката която се кредитира
        """
        # Check for column patterns in Business Navigator template
        expected_keywords = ["док тип", "док номер", "док дата", "счетоводен текст", "сума дебит", "номер на сметка", "име на сметка"]
        return any("счетоводен текст" in h for h in headers) and \
               self._check_keywords_in_headers(headers, expected_keywords, min_matches=4)
    
    def _check_universum_pattern(self, df: pd.DataFrame, headers: List[str]) -> bool:
        """
        Check if the file matches the Universum template pattern
        
        Универсум: columns C, E, F, I, J, K, L, P
        """
        # For Universum, we might need to check the actual data instead of just headers
        # since it's identified by column positions rather than names
        # This is a simplified check that would need to be refined based on actual file samples
        if len(headers) >= 16:  # At least 16 columns (P is the 16th column)
            # Look for patterns in actual data rather than headers
            sample_data = df.iloc[0:5].values.flatten()
            sample_data_str = [str(val).lower() for val in sample_data if not pd.isna(val)]
            
            # Check for accounting-related terms in the data
            accounting_terms = ["дебит", "кредит", "сума", "документ", "операция", "счетоводна"]
            matches = sum(any(term in val for term in accounting_terms) for val in sample_data_str)
            return matches >= 3
        return False
    
    def _check_keywords_in_headers(self, headers: List[str], keywords: List[str], min_matches: int) -> bool:
        """
        Check if at least min_matches keywords are found in the headers
        
        Args:
            headers: List of header strings to check
            keywords: List of keywords to look for
            min_matches: Minimum number of matches required
            
        Returns:
            True if enough matches are found, False otherwise
        """
        print(f"[DEBUG] Checking for {min_matches} matches out of {len(keywords)} keywords")
        
        matches = 0
        matched_keywords = []
        
        for keyword in keywords:
            # Make the comparison case-insensitive and more flexible with whitespace
            if any(keyword.lower() in header.lower() for header in headers):
                matches += 1
                matched_keywords.append(keyword)
        
        print(f"[DEBUG] Found {matches} matches: {matched_keywords}")
        print(f"[DEBUG] Missing keywords: {[k for k in keywords if k not in matched_keywords]}")
        
        result = matches >= min_matches
        print(f"[DEBUG] Keywords match result: {result} ({matches}/{min_matches})")
        
        return result