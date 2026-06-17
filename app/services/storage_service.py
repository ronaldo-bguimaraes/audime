import hashlib
import posixpath
import uuid

import boto3
import requests

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        service_name="s3",
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


def hash_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate_filename() -> str:
    return f"nfce-{uuid.uuid7()}.html"


def download_url(target_url: str) -> bytes:
    session = requests.Session()
    response = session.get(target_url)
    response.raise_for_status()
    return response.content


def upload_to_r2(key: str, data: bytes, metadata: dict | None = None) -> None:
    client = get_s3_client()
    client.put_object(
        Body=data,
        Bucket=settings.r2_storage_bucket,
        Key=key,
        Metadata=metadata or {},
    )
