"""Email MCP server — Gmail API / Microsoft Graph backed."""

from __future__ import annotations

import logging
from typing import Any

from src.config.settings import settings

logger = logging.getLogger(__name__)


class EmailMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {"name": "list", "description": "List recent emails", "inputSchema": {"type": "object", "properties": {"max_results": {"type": "integer", "default": 10}}, "required": []}},
            {"name": "draft", "description": "Draft a new email", "inputSchema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}},
            {"name": "send", "description": "Send an email (requires explicit confirmation)", "inputSchema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}},
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "list":
            return await self._list(int(arguments.get("max_results", 10)))
        elif tool == "draft":
            return await self._draft(str(arguments["to"]), str(arguments["subject"]), str(arguments["body"]))
        elif tool == "send":
            return await self._send(str(arguments["to"]), str(arguments["subject"]), str(arguments["body"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    async def _list(self, max_results: int) -> list[dict[str, Any]]:
        if not settings.email_api_key:
            raise RuntimeError("email_api_key not configured")
        logger.info("email_list", max_results=max_results)
        return []

    async def _draft(self, to: str, subject: str, body: str) -> dict[str, Any]:
        logger.info("email_draft", to=to, subject=subject)
        return {"status": "drafted", "to": to, "subject": subject, "body": body, "requires_confirmation": True}

    async def _send(self, to: str, subject: str, body: str) -> dict[str, Any]:
        logger.info("email_send_blocked", to=to, subject=subject)
        return {"status": "blocked", "reason": "email send requires explicit user confirmation via UI", "to": to, "subject": subject}
