"""Base storage interface."""

from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):
    """Abstract base class for file storage backends."""

    @abstractmethod
    async def save(
        self,
        content: bytes,
        filename: str,
        company_id: str,
    ) -> str:
        """
        Save file content and return storage path.
        
        Args:
            content: File content as bytes
            filename: Original filename
            company_id: Company ID for organizing files
            
        Returns:
            Storage path/key for the saved file
        """
        pass

    @abstractmethod
    async def read(self, path: str) -> bytes:
        """
        Read file content from storage.
        
        Args:
            path: Storage path/key
            
        Returns:
            File content as bytes
        """
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            path: Storage path/key
            
        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            path: Storage path/key
            
        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str | None:
        """
        Get URL for accessing the file.
        
        Args:
            path: Storage path/key
            expires_in: URL expiration time in seconds (for signed URLs)
            
        Returns:
            URL string or None if not applicable
        """
        pass
