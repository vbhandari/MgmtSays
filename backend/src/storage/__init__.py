# Storage module
from src.storage.base import BaseStorage
from src.storage.local_storage import LocalStorage
from src.config.settings import get_settings


def get_storage() -> BaseStorage:
    """Get configured storage backend."""
    settings = get_settings()
    
    if settings.storage_backend == "s3":
        from src.storage.s3_storage import S3Storage
        return S3Storage(
            bucket_name=settings.s3_bucket_name,
            region=settings.aws_region,
        )
    
    return LocalStorage(base_path=settings.upload_dir)


__all__ = ["BaseStorage", "LocalStorage", "get_storage"]
