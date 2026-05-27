from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from src.settings import Settings


@dataclass(frozen=True)
class ClipSpec:
    clip_id: str
    image_path: Path
    prompt: str
    output_path: Path
    seed: int


def generate_clip(
    *,
    settings: Settings,
    model_paths: dict[str, str],
    clip: ClipSpec,
    width: int,
    height: int,
    frames: int,
    fps: float,
) -> dict[str, object]:
    started = time.monotonic()
    cmd = [
        "python",
        "-m",
        "ltx_pipelines.distilled",
        "--distilled-checkpoint-path",
        model_paths["checkpoint_path"],
        "--spatial-upsampler-path",
        model_paths["spatial_upsampler_path"],
        "--gemma-root",
        model_paths["gemma_root"],
        "--prompt",
        clip.prompt,
        "--output-path",
        str(clip.output_path),
        "--seed",
        str(clip.seed),
        "--height",
        str(height),
        "--width",
        str(width),
        "--num-frames",
        str(frames),
        "--frame-rate",
        str(fps),
        "--image",
        str(clip.image_path),
        "0",
        "1.0",
    ]
    if settings.quantization:
        cmd.extend(["--quantization", settings.quantization])
    if settings.offload:
        cmd.extend(["--offload", settings.offload])

    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=60 * 60)
    elapsed = time.monotonic() - started
    return {
        "clip_id": clip.clip_id,
        "returncode": completed.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "output_path": str(clip.output_path),
        "output_exists": clip.output_path.exists(),
        "output_bytes": clip.output_path.stat().st_size if clip.output_path.exists() else 0,
    }
