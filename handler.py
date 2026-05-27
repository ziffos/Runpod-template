from __future__ import annotations

import runpod

from src.worker import handler


runpod.serverless.start({"handler": handler})
