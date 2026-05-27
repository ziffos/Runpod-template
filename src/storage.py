from __future__ import annotations

from pathlib import Path

import boto3
import requests
from botocore.config import Config

from src.settings import Settings


def download_url(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=120, stream=True) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def upload_private_file(settings: Settings, local_path: Path, object_key: str) -> dict[str, str]:
    if not all([
        settings.r2_endpoint_url,
        settings.r2_access_key_id,
        settings.r2_secret_access_key,
        settings.r2_bucket,
    ]):
        raise RuntimeError("R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY and R2_BUCKET are required")

    client = boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    client.upload_file(str(local_path), settings.r2_bucket, object_key, ExtraArgs={"ContentType": "video/mp4"})
    signed_url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.r2_bucket, "Key": object_key},
        ExpiresIn=60 * 60 * 24,
    )
    return {"bucket": settings.r2_bucket, "key": object_key, "signed_url": signed_url}
