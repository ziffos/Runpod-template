from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    model_root: Path
    checkpoint_filename: str
    upscaler_filename: str
    gemma_repo: str
    gemma_root: Path
    quantization: str
    offload: str
    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket: str


def get_settings() -> Settings:
    model_root = Path(os.environ.get("LTX_MODEL_ROOT", "/runpod-volume/models/ltx-2.3"))
    return Settings(
        model_root=model_root,
        checkpoint_filename=os.environ.get(
            "LTX_CHECKPOINT_FILENAME",
            "ltx-2.3-22b-distilled-1.1.safetensors",
        ),
        upscaler_filename=os.environ.get(
            "LTX_SPATIAL_UPSCALER_FILENAME",
            "ltx-2.3-spatial-upscaler-x2-1.1.safetensors",
        ),
        gemma_repo=os.environ.get("LTX_GEMMA_REPO", "google/gemma-3-12b-it"),
        gemma_root=Path(os.environ.get("LTX_GEMMA_ROOT", str(model_root / "gemma-3-12b-it"))),
        quantization=os.environ.get("LTX_QUANTIZATION", "fp8-cast"),
        offload=os.environ.get("LTX_OFFLOAD", "cpu"),
        r2_endpoint_url=os.environ.get("R2_ENDPOINT_URL", ""),
        r2_access_key_id=os.environ.get("R2_ACCESS_KEY_ID", ""),
        r2_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
        r2_bucket=os.environ.get("R2_BUCKET", ""),
    )
