"""Utility helper functions."""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)
    # Remove leading/trailing hyphens
    return text.strip("-")


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be safe for filesystem storage."""
    # Get just the filename, not the path
    filename = Path(filename).name
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = f"{name[:200-len(ext)-1]}.{ext}" if ext else name[:200]
    return filename


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def extract_quarter_year(date: datetime) -> tuple[int, int]:
    """Extract quarter and year from a datetime."""
    quarter = (date.month - 1) // 3 + 1
    return quarter, date.year


def format_quarter(quarter: int, year: int) -> str:
    """Format quarter and year as string (e.g., 'Q2 2024')."""
    return f"Q{quarter} {year}"


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def chunk_list(lst: list[Any], chunk_size: int) -> list[list[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """Remove keys with None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}
