"""Local filesystem storage implementation."""

import os
import aiofiles
from pathlib import Path
from datetime import datetime

from src.storage.base import BaseStorage
from src.utils.helpers import generate_uuid


class LocalStorage(BaseStorage):
    """Local filesystem storage backend."""

    def __init__(self, base_path: str = "./uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        content: bytes,
        filename: str,
        company_id: str,
    ) -> str:
        """Save file to local filesystem."""
        # Create company directory
        company_dir = self.base_path / company_id
        company_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = generate_uuid()[:8]
        ext = Path(filename).suffix
        new_filename = f"{timestamp}_{unique_id}{ext}"

        # Full path
        file_path = company_dir / new_filename

        # Write file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # Return relative path
        return str(file_path.relative_to(self.base_path))

    async def read(self, path: str) -> bytes:
        """Read file from local filesystem."""
        file_path = self.base_path / path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def delete(self, path: str) -> bool:
        """Delete file from local filesystem."""
        file_path = self.base_path / path

        if not file_path.exists():
            return False

        os.remove(file_path)
        return True

    async def exists(self, path: str) -> bool:
        """Check if file exists in local filesystem."""
        file_path = self.base_path / path
        return file_path.exists()

    async def get_url(self, path: str, expires_in: int = 3600) -> str | None:
        """
        Get URL for local file.
        
        For local storage, this returns a file:// URL or None
        depending on the use case.
        """
        file_path = self.base_path / path
        if file_path.exists():
            return f"file://{file_path.absolute()}"
        return None

    def get_full_path(self, path: str) -> Path:
        """Get full filesystem path."""
        return self.base_path / path
