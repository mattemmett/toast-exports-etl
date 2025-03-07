import pytest
from file_processors.orders_processor import format_server_name

def test_format_server_name():
    """Test the format_server_name function with various inputs."""
    # Test basic two-word name
    assert format_server_name("Bartender A") == "A, Bartender"
    assert format_server_name("John Doe") == "Doe, John"
    
    # Test with leading/trailing spaces
    assert format_server_name("  Bartender A  ") == "A, Bartender"
    
    # Test with multiple first names
    assert format_server_name("John James Doe") == "Doe, John James"
    
    # Test edge cases
    assert format_server_name("") is None
    assert format_server_name(None) is None
    assert format_server_name("SingleName") == "SingleName"  # No change if can't split
    
    # Test non-string input
    assert format_server_name(123) is None
    
    # Test with multiple spaces between words
    assert format_server_name("Bartender   A") == "A, Bartender" 