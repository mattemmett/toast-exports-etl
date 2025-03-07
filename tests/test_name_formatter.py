import pytest
from utils.name_formatter import format_name

def test_format_name():
    """Test the format_name function with various inputs."""
    # Test basic name formatting
    assert format_name("Bartender A") == "A, Bartender"
    assert format_name("John Doe") == "Doe, John"
    
    # Test names that are already in correct format
    assert format_name("Doe, John") == "Doe, John"
    assert format_name("A, Bartender") == "A, Bartender"
    
    # Test names with multiple parts
    assert format_name("John James Doe") == "Doe, John James"
    assert format_name("Mary Jane Smith") == "Smith, Mary Jane"
    
    # Test edge cases
    assert format_name("") is None
    assert format_name(None) is None
    assert format_name("SingleName") == "SingleName"
    
    # Test with leading/trailing spaces
    assert format_name("  John   Doe  ") == "Doe, John"
    assert format_name("  Doe,   John  ") == "Doe,   John"
    
    # Test with multiple spaces between words
    assert format_name("John    Doe") == "Doe, John"
    assert format_name("Mary   Jane   Smith") == "Smith, Mary Jane" 