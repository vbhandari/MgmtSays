"""AWS S3 storage implementation."""

from src.storage.base import BaseStorage
from src.config.settings import get_settings


class S3Storage(BaseStorage):
    """AWS S3 storage backend."""

    def __init__(self, bucket_name: str | None = None, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self._client = None

    @property
    def client(self):
        """Get or create S3 client."""
        if self._client is None:
            import boto3
            settings = get_settings()
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
        return self._client

    async def save(
        self,
        content: bytes,
        filename: str,
        company_id: str,
    ) -> str:
        """Save file to S3."""
        from datetime import datetime
        from src.utils.helpers import generate_uuid
        from pathlib import Path

        # Generate unique key
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = generate_uuid()[:8]
        ext = Path(filename).suffix
        key = f"{company_id}/{timestamp}_{unique_id}{ext}"

        # Upload to S3
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content,
        )

        return key

    async def read(self, path: str) -> bytes:
        """Read file from S3."""
        response = self.client.get_object(
            Bucket=self.bucket_name,
            Key=path,
        )
        return response["Body"].read()

    async def delete(self, path: str) -> bool:
        """Delete file from S3."""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=path,
            )
            return True
        except Exception:
            return False

    async def exists(self, path: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=path,
            )
            return True
        except Exception:
            return False

    async def get_url(self, path: str, expires_in: int = 3600) -> str | None:
        """Get presigned URL for S3 object."""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": path,
                },
                ExpiresIn=expires_in,
            )
            return url
        except Exception:
            return None
