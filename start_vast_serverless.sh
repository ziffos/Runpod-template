#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

if [[ "${HF_HOME:-}" == /runpod-volume/* && ! -d /runpod-volume ]]; then
  unset HF_HOME
fi
if [[ "${HUGGINGFACE_HUB_CACHE:-}" == /runpod-volume/* && ! -d /runpod-volume ]]; then
  unset HUGGINGFACE_HUB_CACHE
fi
if [[ "${LTX_MODEL_ROOT:-}" == /runpod-volume/* && ! -d /runpod-volume ]]; then
  unset LTX_MODEL_ROOT
fi

export HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-/workspace/.cache/huggingface/hub}"
export LTX_MODEL_ROOT="${LTX_MODEL_ROOT:-/workspace/models/ltx-2.3}"

mkdir -p "$(dirname /tmp/ltx-model-server.log)" "$HF_HOME" "$LTX_MODEL_ROOT"
touch /tmp/ltx-model-server.log

python -m uvicorn src.model_server:app --host 127.0.0.1 --port 18000 >> /tmp/ltx-model-server.log 2>&1 &
exec python -u /vast_worker.py
