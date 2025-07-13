# Utility functions for the backend
import os
from typing import Optional

def validate_file_type(filename: str, allowed_extensions: list = ['.pdf']) -> bool:
    """
    Validate if file type is supported.
    
    Args:
        filename: Name of uploaded file
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if file type is supported, False otherwise
    """
    file_ext = os.path.splitext(filename)[1].lower()
    return file_ext in allowed_extensions 