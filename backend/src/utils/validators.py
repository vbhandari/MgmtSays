"""Input validation utilities."""

import re
from pathlib import Path

# Common regex patterns
TICKER_PATTERN = re.compile(r"^[A-Z]{1,5}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Allowed file extensions for document upload
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt"}

# Maximum file sizes (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def is_valid_ticker(ticker: str) -> bool:
    """Validate stock ticker symbol."""
    return bool(TICKER_PATTERN.match(ticker.upper()))


def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    return bool(EMAIL_PATTERN.match(email))


def is_allowed_document_type(filename: str) -> bool:
    """Check if file extension is allowed for document upload."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_DOCUMENT_EXTENSIONS


def get_document_type(filename: str) -> str | None:
    """Get document type from filename extension."""
    ext = Path(filename).suffix.lower()
    type_mapping = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".doc": "docx",
        ".pptx": "pptx",
        ".ppt": "pptx",
        ".txt": "txt",
    }
    return type_mapping.get(ext)


def validate_file_size(size_bytes: int, max_size: int = MAX_FILE_SIZE) -> bool:
    """Validate file size is within limits."""
    return 0 < size_bytes <= max_size


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection attacks."""
    # Remove potentially dangerous characters
    query = re.sub(r"[<>\"'%;()&+]", "", query)
    # Limit length
    return query[:500].strip()


def validate_date_range(start_date: str | None, end_date: str | None) -> tuple[bool, str | None]:
    """Validate date range format and logic."""
    from datetime import datetime

    date_format = "%Y-%m-%d"
    
    if start_date:
        try:
            start = datetime.strptime(start_date, date_format)
        except ValueError:
            return False, "Invalid start_date format. Use YYYY-MM-DD."
    else:
        start = None
    
    if end_date:
        try:
            end = datetime.strptime(end_date, date_format)
        except ValueError:
            return False, "Invalid end_date format. Use YYYY-MM-DD."
    else:
        end = None
    
    if start and end and start > end:
        return False, "start_date must be before end_date."
    
    return True, None


def validate_pagination(
    page: int,
    page_size: int,
    max_page_size: int = 100,
) -> tuple[bool, str | None]:
    """Validate pagination parameters."""
    if page < 1:
        return False, "Page must be >= 1"
    if page_size < 1:
        return False, "Page size must be >= 1"
    if page_size > max_page_size:
        return False, f"Page size must be <= {max_page_size}"
    return True, None
