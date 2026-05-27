from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any

from src.ltx import ClipSpec, generate_clip
from src.models import ensure_models
from src.settings import get_settings
from src.storage import download_url, upload_private_file


DEFAULT_WIDTH = 704
DEFAULT_HEIGHT = 1280
DEFAULT_FRAMES = 113
DEFAULT_FPS = 16.0


def handler(job: dict[str, Any]) -> dict[str, Any]:
    job_input = job.get("input") or {}
    if job_input.get("healthcheck"):
        return {"ok": True, "worker": "sweden-brief-ltx"}

    settings = get_settings()
    run_id = str(job_input.get("run_id", f"run-{int(time.time())}"))
    output_prefix = str(job_input.get("output_prefix", f"sweden-brief/runs/{run_id}")).strip("/")
    width = int(job_input.get("width", DEFAULT_WIDTH))
    height = int(job_input.get("height", DEFAULT_HEIGHT))
    frames = int(job_input.get("frames", DEFAULT_FRAMES))
    fps = float(job_input.get("fps", DEFAULT_FPS))
    clips = job_input.get("clips") or []

    if not clips:
        raise ValueError("input.clips must contain at least one clip")
    if width % 64 or height % 64:
        raise ValueError("width and height must be divisible by 64 for the distilled two-stage pipeline")
    if (frames - 1) % 8:
        raise ValueError("frames must satisfy frames = 8k + 1")

    model_paths = ensure_models(settings)
    outputs = []
    with tempfile.TemporaryDirectory(prefix="ltx-run-") as temp_dir:
        work_dir = Path(temp_dir)
        for index, clip in enumerate(clips, start=1):
            clip_id = str(clip.get("clip_id", f"clip-{index:02d}"))
            image_url = clip.get("image_url")
            prompt = clip.get("prompt")
            if not image_url or not prompt:
                raise ValueError("each clip needs image_url and prompt")

            image_path = work_dir / f"{clip_id}.png"
            output_path = work_dir / f"{clip_id}.mp4"
            download_url(str(image_url), image_path)
            generation = generate_clip(
                settings=settings,
                model_paths=model_paths,
                clip=ClipSpec(
                    clip_id=clip_id,
                    image_path=image_path,
                    prompt=str(prompt),
                    output_path=output_path,
                    seed=int(clip.get("seed", 1000 + index)),
                ),
                width=width,
                height=height,
                frames=frames,
                fps=fps,
            )
            if generation["returncode"] != 0 or not output_path.exists():
                outputs.append({"clip_id": clip_id, "status": "failed", "generation": generation})
                continue

            object_key = f"{output_prefix}/{clip_id}.mp4"
            uploaded = upload_private_file(settings, output_path, object_key)
            outputs.append({
                "clip_id": clip_id,
                "status": "succeeded",
                "generation": generation,
                "output": uploaded,
            })

    failed = [item for item in outputs if item["status"] != "succeeded"]
    return {
        "run_id": run_id,
        "model": settings.checkpoint_filename,
        "width": width,
        "height": height,
        "frames": frames,
        "fps": fps,
        "outputs": outputs,
        "succeeded": len(outputs) - len(failed),
        "failed": len(failed),
    }
