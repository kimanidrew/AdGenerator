"""Cloudflare R2 access through its S3-compatible API.

Keep this module server-side. Never expose R2 credentials to the browser.
Use short-lived presigned URLs for browser uploads and downloads.
"""
from functools import lru_cache

import boto3
from botocore.config import Config

from app.config import settings


@lru_cache
def get_storage_client():
    if settings.storage_provider.lower() not in {"cloudflare_r2", "s3"}:
        raise RuntimeError(
            f"Unsupported storage provider: {settings.storage_provider}"
        )

    endpoint = settings.effective_storage_endpoint
    required = {
        "R2 S3 API endpoint (STORAGE_ENDPOINT or R2_ACCOUNT_ID)": endpoint,
        "STORAGE_BUCKET": settings.storage_bucket,
        "STORAGE_ACCESS_KEY": settings.storage_access_key,
        "STORAGE_SECRET_KEY": settings.storage_secret_key,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Object storage is not configured. Missing: " + ", ".join(missing)
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=settings.storage_region or "auto",
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


def create_upload_url(
    object_key: str,
    content_type: str,
    expires_in: int = 900,
) -> str:
    """Create a short-lived URL for uploading one object to the private bucket."""
    if not object_key or not content_type:
        raise ValueError("object_key and content_type are required")
    return get_storage_client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.storage_bucket,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )


def upload_bytes(object_key: str, content: bytes, content_type: str) -> None:
    """Upload generated media to the private R2 bucket."""
    if not object_key or not content or not content_type:
        raise ValueError("object_key, content and content_type are required")
    get_storage_client().put_object(
        Bucket=settings.storage_bucket, Key=object_key, Body=content, ContentType=content_type
    )


def create_download_url(object_key: str, expires_in: int = 900) -> str:
    """Create a short-lived URL for downloading one object from the private bucket."""
    if not object_key:
        raise ValueError("object_key is required")
    return get_storage_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.storage_bucket, "Key": object_key},
        ExpiresIn=expires_in,
    )
