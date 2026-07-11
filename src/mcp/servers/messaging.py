"""Messaging MCP server — WhatsApp/Slack/Telegram/SMS unified surface."""

from __future__ import annotations

import logging
from typing import Any

from src.config.settings import settings

logger = logging.getLogger(__name__)


class MessagingMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {"name": "list_channels", "description": "List available messaging channels", "inputSchema": {"type": "object", "properties": {}, "required": []}},
            {"name": "draft", "description": "Draft a message", "inputSchema": {"type": "object", "properties": {"channel": {"type": "string"}, "recipient": {"type": "string"}, "body": {"type": "string"}}, "required": ["channel", "recipient", "body"]}},
            {"name": "send", "description": "Send a message (requires explicit confirmation)", "inputSchema": {"type": "object", "properties": {"channel": {"type": "string"}, "recipient": {"type": "string"}, "body": {"type": "string"}}, "required": ["channel", "recipient", "body"]}},
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "list_channels":
            return self._list_channels()
        elif tool == "draft":
            return await self._draft(str(arguments["channel"]), str(arguments["recipient"]), str(arguments["body"]))
        elif tool == "send":
            return await self._send(str(arguments["channel"]), str(arguments["recipient"]), str(arguments["body"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    def _list_channels(self) -> list[dict[str, Any]]:
        return [
            {"channel": "whatsapp", "status": "configured" if settings.email_api_key else "needs_api_key"},
            {"channel": "slack", "status": "needs_api_key"},
            {"channel": "telegram", "status": "needs_api_key"},
            {"channel": "sms", "status": "needs_api_key"},
        ]

    async def _draft(self, channel: str, recipient: str, body: str) -> dict[str, Any]:
        logger.info("message_draft", channel=channel, recipient=recipient)
        return {"status": "drafted", "channel": channel, "recipient": recipient, "body": body, "requires_confirmation": True}

    async def _send(self, channel: str, recipient: str, body: str) -> dict[str, Any]:
        logger.info("message_send_blocked", channel=channel, recipient=recipient)
        return {"status": "blocked", "reason": "message send requires explicit user confirmation via UI", "channel": channel, "recipient": recipient}
