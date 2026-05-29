from __future__ import annotations

from typing import Any

from vastai import BenchmarkConfig, HandlerConfig, LogActionConfig, Worker, WorkerConfig


MODEL_SERVER_URL = "http://127.0.0.1"
MODEL_SERVER_PORT = 18000
MODEL_LOG_FILE = "/tmp/ltx-model-server.log"


def request_parser(json_msg: dict[str, Any]) -> dict[str, Any]:
    return json_msg.get("payload") or json_msg.get("input") or json_msg


def workload(payload: dict[str, Any]) -> float:
    width = int(payload.get("width", 704))
    height = int(payload.get("height", 1280))
    frames = int(payload.get("frames", 113))
    clips = max(1, len(payload.get("clips") or [1]))
    return clips * frames * width * height / 1_000_000


worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    handlers=[
        HandlerConfig(
            route="/health",
            allow_parallel_requests=True,
            max_queue_time=30.0,
            workload_calculator=lambda payload: 1.0,
            benchmark_config=BenchmarkConfig(dataset=[{"healthcheck": True}], runs=1, concurrency=1),
            request_parser=request_parser,
        ),
        HandlerConfig(
            route="/generate",
            allow_parallel_requests=False,
            max_queue_time=900.0,
            workload_calculator=workload,
            request_parser=request_parser,
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=["Application startup complete."],
        on_error=["Traceback (most recent call last):", "Generation failed"],
        on_info=["INFO"],
    ),
)


Worker(worker_config).run()
