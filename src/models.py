from __future__ import annotations

from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download

from src.settings import Settings


LTX_REPO = "Lightricks/LTX-2.3"


def ensure_models(settings: Settings) -> dict[str, str]:
    settings.model_root.mkdir(parents=True, exist_ok=True)
    checkpoint_path = settings.model_root / settings.checkpoint_filename
    upscaler_path = settings.model_root / settings.upscaler_filename

    if not checkpoint_path.exists():
        hf_hub_download(
            repo_id=LTX_REPO,
            filename=settings.checkpoint_filename,
            local_dir=settings.model_root,
        )
    if not upscaler_path.exists():
        hf_hub_download(
            repo_id=LTX_REPO,
            filename=settings.upscaler_filename,
            local_dir=settings.model_root,
        )
    if not settings.gemma_root.exists() or not any(Path(settings.gemma_root).iterdir()):
        snapshot_download(
            repo_id=settings.gemma_repo,
            local_dir=settings.gemma_root,
            local_dir_use_symlinks=False,
        )

    return {
        "checkpoint_path": str(checkpoint_path),
        "spatial_upsampler_path": str(upscaler_path),
        "gemma_root": str(settings.gemma_root),
    }
