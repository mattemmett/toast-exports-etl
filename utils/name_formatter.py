"""
Utility functions for formatting names consistently across the application.
"""

def format_name(name):
    """
    Convert name between 'Firstname Lastname' and 'Lastname, Firstname' formats.
    If the name is already in 'Lastname, Firstname' format, it will be returned as is.
    
    Args:
        name (str): The name to format
        
    Returns:
        str: The formatted name or None if input is invalid
        
    Examples:
        'Bartender A' -> 'A, Bartender'
        'John Doe' -> 'Doe, John'
        'Doe, John' -> 'Doe, John'
    """
    if not name or not isinstance(name, str):
        return None
        
    name = name.strip()
    
    # If already in "Lastname, Firstname" format, return as is
    if ',' in name:
        return name
        
    parts = name.split()
    if len(parts) < 2:
        return name
        
    # Take the last word as the last name, join all other words as first name
    last_name = parts[-1]
    first_name = ' '.join(parts[:-1])
    return f"{last_name}, {first_name}" 