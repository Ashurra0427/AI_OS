"""Coding agent — writes/debugs/refactors code, runs builds."""

from __future__ import annotations

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.security.sandbox import SandboxedShell

logger = logging.getLogger(__name__)


class CodingAgent(BaseAgent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("name", "coding")
        super().__init__(*args, **kwargs)
        self._sandbox = SandboxedShell(allowed_dirs=["/project", str(__import__('pathlib').Path.cwd())])

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        self.log("code_task", task=str(task)[:200])
        action = task.get("action", "write")
        if action == "write":
            return await self._write_code(task)
        elif action == "run":
            return self._sandbox.run(str(task.get("command", "")))
        return {"status": "unknown_action"}

    async def _write_code(self, task: dict[str, Any]) -> dict[str, Any]:
        path = str(task.get("path", "/project/main.py"))
        content = str(task.get("content", "# TODO\n"))
        result = self._sandbox._write_file(path, content)
        return {"status": "written", "path": path, "result": result}
