from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException

from src.job import healthcheck, process_job_input


logging.basicConfig(
    filename="/tmp/ltx-model-server.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("ltx-model-server")

app = FastAPI(title="Sweden Brief LTX Worker")


@app.on_event("startup")
async def startup() -> None:
    logger.info("Application startup complete.")


@app.get("/health")
async def get_health() -> dict[str, Any]:
    return healthcheck()


@app.post("/health")
async def post_health() -> dict[str, Any]:
    return healthcheck()


@app.post("/generate")
async def generate(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return process_job_input(payload)
    except Exception as exc:  # noqa: BLE001 - surface failures to PyWorker/orchestrator.
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=repr(exc)) from exc
