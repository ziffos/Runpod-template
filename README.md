# Sweden Brief RunPod LTX Worker

RunPod Serverless worker for generating Sweden Brief image-to-video clips with LTX-2.3.

## Model

Default checkpoint: `Lightricks/LTX-2.3` / `ltx-2.3-22b-distilled-1.1.safetensors`.

The worker uses `ltx_pipelines.distilled` from the official `Lightricks/LTX-2` repo, with:

- `704x1280` portrait output
- `113` frames
- `16` fps
- about `7.06s` per clip
- `fp8-cast` quantization by default
- `cpu` offload by default for RTX 4090 safety

## Required RunPod Endpoint Setup

Create a RunPod Serverless endpoint using GitHub integration pointed at this repo.

Recommended endpoint settings:

- GPU: RTX 4090
- Max workers: 4
- Idle timeout: 5-10 minutes while benchmarking
- Execution timeout: at least 60 minutes
- Attach a network volume mounted at `/runpod-volume`

Create the network volume in the same region/data center you want to run the endpoint in. Start with at least `150 GB` because LTX-2.3, Gemma 3 12B, upscaler files, Hugging Face cache, and temporary build artifacts are large.

## Required Environment Variables

Set these on the RunPod endpoint:

```text
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=...
HF_TOKEN=...
HF_HOME=/runpod-volume/huggingface
HUGGINGFACE_HUB_CACHE=/runpod-volume/huggingface/hub
LTX_MODEL_ROOT=/runpod-volume/models/ltx-2.3
LTX_CHECKPOINT_FILENAME=ltx-2.3-22b-distilled-1.1.safetensors
LTX_SPATIAL_UPSCALER_FILENAME=ltx-2.3-spatial-upscaler-x2-1.1.safetensors
LTX_GEMMA_REPO=google/gemma-3-12b-it
LTX_GEMMA_ROOT=/runpod-volume/models/ltx-2.3/gemma-3-12b-it
LTX_QUANTIZATION=fp8-cast
LTX_OFFLOAD=cpu
```

You must accept any required Hugging Face licenses for `Lightricks/LTX-2.3` and `google/gemma-3-12b-it` on the Hugging Face account behind `HF_TOKEN`.

## Job Input

Each job should contain two clips. Sweden Brief sends four async RunPod jobs for eight clips total.

```json
{
  "input": {
    "run_id": "sweden-brief-2026-05-27",
    "output_prefix": "sweden-brief/runs/sweden-brief-2026-05-27",
    "width": 704,
    "height": 1280,
    "frames": 113,
    "fps": 16,
    "clips": [
      {
        "clip_id": "scene-01",
        "image_url": "signed R2 input URL",
        "prompt": "Subtle documentary camera push-in. Preserve the image. Minimal motion. No text."
      }
    ]
  }
}
```
