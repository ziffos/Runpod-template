FROM runpod/pytorch:1.0.3-cu1281-torch280-ubuntu2204 AS base

ENV DEBIAN_FRONTEND=noninteractive     PYTHONUNBUFFERED=1     PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True     HF_HOME=/runpod-volume/huggingface     HUGGINGFACE_HUB_CACHE=/runpod-volume/huggingface/hub     LTX_MODEL_ROOT=/runpod-volume/models/ltx-2.3     HF_HUB_DISABLE_XET=1

RUN apt-get update &&     apt-get install -y --no-install-recommends git ffmpeg curl ca-certificates &&     rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip uv &&     pip install --no-cache-dir -r /requirements.txt

RUN git clone --depth 1 https://github.com/Lightricks/LTX-2.git /opt/LTX-2 &&     cd /opt/LTX-2 &&     uv sync --frozen &&     . .venv/bin/activate &&     pip install --no-cache-dir -e packages/ltx-core -e packages/ltx-pipelines

WORKDIR /
COPY handler.py /handler.py
COPY vast_worker.py /vast_worker.py
COPY start_vast_serverless.sh /start_vast_serverless.sh
COPY src /src
RUN chmod +x /start_vast_serverless.sh

FROM base AS vast
CMD ["/start_vast_serverless.sh"]

FROM base AS runpod
CMD ["python", "-u", "/handler.py"]
