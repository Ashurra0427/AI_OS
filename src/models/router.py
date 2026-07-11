"""MoE Router — routes requests to the best model or agent."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MoERouter:
    def __init__(self) -> None:
        self._local_rules: list[tuple[str, bool]] = []
        self._cloud_models = ["gpt-4o", "claude-3-5-sonnet"]
        self._local_models = ["Qwen/Qwen2.5-0.5B-Instruct"]

    def add_local_rule(self, keyword: str) -> None:
        self._local_rules.append((keyword, True))

    async def route(self, request: dict[str, Any]) -> dict[str, Any]:
        text = str(request.get("text", "")).lower()
        for keyword, _ in self._local_rules:
            if keyword.lower() in text:
                return {"target": "local", "model": self._local_models[0]}
        return {"target": "cloud", "model": self._cloud_models[0]}
