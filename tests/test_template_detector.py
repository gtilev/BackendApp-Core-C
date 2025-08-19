import os
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from app.services.template_detector import TemplateDetector, TemplateType


@pytest.fixture
def template_detector():
    return TemplateDetector()


def test_get_headers():
    """Test the _get_headers method"""
    detector = TemplateDetector()
    # Create a sample DataFrame with headers
    data = {"Column1": [], "Column2": [], "дебит": [], "кредит": []}
    df = pd.DataFrame(data)
    
    headers = detector._get_headers(df)
    
    assert len(headers) == 4
    assert "column1" in headers
    assert "column2" in headers
    assert "дебит" in headers
    assert "кредит" in headers


@patch("pandas.read_excel")
def test_detect_rival_template(mock_read_excel, template_detector):
    """Test detection of Rival template"""
    # Create a mock DataFrame that looks like a Rival template
    mock_df = pd.DataFrame({
        0: ["вид документ", "ФА", "ФА"],
        1: ["номер на документ", "123", "456"],
        2: ["дата", "01.01.2023", "02.01.2023"],
        3: ["име", "Company A", "Company B"],
        4: ["дебит", "101", "102"],
        5: ["кредит", "201", "202"],
        6: ["сума", 1000, 2000],
        7: ["обяснение", "Payment", "Invoice"]
    })
    
    # Configure the mock to return our DataFrame
    mock_read_excel.return_value = mock_df
    
    # Test with a mock file path
    result = template_detector.detect_template("mock_path.xlsx")
    
    # Verify the result
    assert result == TemplateType.RIVAL
    
    # Verify read_excel was called
    mock_read_excel.assert_called_once_with("mock_path.xlsx", nrows=10)


@patch("pandas.read_excel")
def test_detect_unknown_template(mock_read_excel, template_detector):
    """Test detection of an unknown template"""
    # Create a mock DataFrame that doesn't match any template
    mock_df = pd.DataFrame({
        0: ["Random", "Data", "Here"],
        1: ["More", "Random", "Stuff"]
    })
    
    # Configure the mock to return our DataFrame
    mock_read_excel.return_value = mock_df
    
    # Test with a mock file path
    result = template_detector.detect_template("mock_path.xlsx")
    
    # Verify the result
    assert result is None


@patch("pandas.read_excel")
def test_handle_exception(mock_read_excel, template_detector):
    """Test handling of exceptions during template detection"""
    # Configure the mock to raise an exception
    mock_read_excel.side_effect = Exception("Test exception")
    
    # Test with a mock file path
    result = template_detector.detect_template("mock_path.xlsx")
    
    # Verify the result
    assert result is None