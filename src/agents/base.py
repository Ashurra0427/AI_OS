"""Base agent class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import structlog

logger = structlog.get_logger()


class BaseAgent(ABC):
    def __init__(self, name: str, mcp_client: Any | None = None) -> None:
        self.name = name
        self._mcp = mcp_client

    @abstractmethod
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        ...

    async def call_mcp(self, server: str, tool: str, arguments: dict[str, Any]) -> Any:
        if self._mcp is None:
            raise RuntimeError("MCP client not configured")
        return await self._mcp.call_tool(server, tool, arguments)

    def log(self, event: str, **kwargs: Any) -> None:
        logger.info("agent_event", agent=self.name, event_type=event, **kwargs)
