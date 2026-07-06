import io
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, BinaryIO

from app.config import settings

logger = logging.getLogger("storage")

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError

    _s3_available = bool(settings.aws_access_key_id and settings.aws_secret_access_key)
except ImportError:
    _s3_available = False

S3_BUCKET = settings.s3_bucket or "jobsearch-resumes"
S3_REGION = settings.s3_region or "us-east-1"
S3_ENDPOINT = settings.s3_endpoint or None
PRESIGNED_URL_EXPIRY = 3600  # 1 hour

_local_store: dict[str, bytes] = {}


def _get_s3_client():
    if not _s3_available:
        return None
    kwargs = {
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
        "region_name": S3_REGION,
        "config": Config(signature_version="s3v4"),
    }
    if S3_ENDPOINT:
        kwargs["endpoint_url"] = S3_ENDPOINT
    return boto3.client("s3", **kwargs)


def upload_resume(file_bytes: bytes, filename: str) -> dict:
    file_id = str(uuid.uuid4())
    key = f"resumes/{file_id}/{filename}"

    s3 = _get_s3_client()
    if s3:
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=key, Body=file_bytes, ServerSideEncryption="aws:kms")
            logger.info("Uploaded resume to S3: %s", key)
        except ClientError as e:
            logger.error("S3 upload failed: %s", e)
            # Fall through to local storage
        else:
            return {"file_id": file_id, "key": key, "storage": "s3"}

    # Fallback: in-memory storage
    _local_store[key] = file_bytes
    logger.warning("Stored resume locally (no S3): %s", key)
    return {"file_id": file_id, "key": key, "storage": "local"}


def get_presigned_download_url(key: str) -> Optional[str]:
    s3 = _get_s3_client()
    if s3:
        try:
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_BUCKET, "Key": key},
                ExpiresIn=PRESIGNED_URL_EXPIRY,
            )
            return url
        except ClientError as e:
            logger.error("Failed to generate presigned URL: %s", e)
            return None
    return None


def get_resume_bytes(key: str) -> Optional[bytes]:
    s3 = _get_s3_client()
    if s3:
        try:
            resp = s3.get_object(Bucket=S3_BUCKET, Key=key)
            return resp["Body"].read()
        except ClientError as e:
            logger.error("S3 get failed: %s", e)
            return None

    return _local_store.get(key)
