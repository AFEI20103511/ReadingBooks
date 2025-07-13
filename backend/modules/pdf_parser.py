# PDF parsing utilities using pdfplumber
import pdfplumber
from typing import Optional

def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        # Create a temporary file-like object from bytes
        import io
        file_stream = io.BytesIO(file_content)
        
        # Extract text from PDF
        with pdfplumber.open(file_stream) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None

def get_text_preview(text: str, max_length: int = 500) -> str:
    """
    Get a preview of the extracted text.
    
    Args:
        text: Full extracted text
        max_length: Maximum length of preview
        
    Returns:
        Text preview
    """
    if not text:
        return ""
    return text[:max_length] + ("..." if len(text) > max_length else "") 