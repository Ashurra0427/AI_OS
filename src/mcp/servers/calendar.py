"""Calendar MCP server."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CalendarMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {"name": "list_events", "description": "List calendar events", "inputSchema": {"type": "object", "properties": {"start": {"type": "string"}, "end": {"type": "string"}}, "required": []}},
            {"name": "create_event", "description": "Create a calendar event (requires confirmation)", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "start": {"type": "string"}, "end": {"type": "string"}, "attendees": {"type": "array", "items": {"type": "string"}}}, "required": ["title", "start", "end"]}},
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "list_events":
            return await self._list_events(str(arguments.get("start", "")), str(arguments.get("end", "")))
        elif tool == "create_event":
            return await self._create_event(str(arguments["title"]), str(arguments["start"]), str(arguments["end"]), arguments.get("attendees", []))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    async def _list_events(self, start: str, end: str) -> list[dict[str, Any]]:
        logger.info("calendar_list", start=start, end=end)
        return []

    async def _create_event(self, title: str, start: str, end: str, attendees: list[str]) -> dict[str, Any]:
        logger.info("calendar_create_blocked", title=title)
        return {"status": "blocked", "reason": "calendar event creation requires explicit user confirmation via UI", "title": title, "start": start, "end": end, "attendees": attendees}
