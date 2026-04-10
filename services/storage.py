from __future__ import annotations

import os
from datetime import datetime

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class StorageError(Exception):
    pass


def _build_object_key(prefix: str, filename: str) -> str:
    now = datetime.utcnow()
    safe_prefix = prefix.strip("/")
    return f"{safe_prefix}/{now:%Y/%m}/{filename}"


def upload_file_to_s3(local_path: str, filename: str, bucket: str, region: str, prefix: str) -> str:
    if not bucket:
        raise StorageError("AWS_S3_BUCKET is required for S3 storage backend")

    object_key = _build_object_key(prefix, filename)
    client = boto3.client("s3", region_name=region)

    try:
        content_type = "application/octet-stream"
        lower = filename.lower()
        if lower.endswith(".pdf"):
            content_type = "application/pdf"
        elif lower.endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        client.upload_file(
            local_path,
            bucket,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )
    except (BotoCoreError, ClientError) as exc:
        raise StorageError(f"S3 upload failed: {exc}") from exc

    return f"s3://{bucket}/{object_key}"


def maybe_remove_local_file(local_path: str) -> None:
    try:
        if os.path.exists(local_path):
            os.remove(local_path)
    except OSError:
        # Best-effort cleanup; not fatal to resume processing.
        pass
