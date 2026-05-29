from __future__ import annotations

from typing import Any

from src.job import process_job_input


def handler(job: dict[str, Any]) -> dict[str, Any]:
    return process_job_input(job.get("input") or {})
