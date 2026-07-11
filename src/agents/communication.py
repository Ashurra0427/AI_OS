"""Communication agent — email and messaging with draft-then-confirm."""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.security.audit import log_agent_action


class CommunicationAgent(BaseAgent):
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        self.log("communicate", task=str(task)[:200])
        action = task.get("action", "draft")
        if action == "draft":
            return await self._draft(task)
        elif action == "send":
            return await self._send(task)
        elif action == "list":
            return await self._list(task)
        return {"status": "unknown_action"}

    async def _draft(self, task: dict[str, Any]) -> dict[str, Any]:
        channel = str(task.get("channel", "email"))
        recipient = str(task.get("to", task.get("recipient", "")))
        subject = str(task.get("subject", ""))
        body = str(task.get("body", ""))
        if self._mcp:
            try:
                if channel == "email":
                    result = await self.call_mcp("email", "draft", {"to": recipient, "subject": subject, "body": body})
                else:
                    result = await self.call_mcp("messaging", "draft", {"channel": channel, "recipient": recipient, "body": body})
                log_agent_action(self.name, "draft", {"channel": channel, "recipient": recipient})
                return result
            except Exception as exc:
                self.log("draft_error", error=str(exc))
        return {"status": "drafted", "channel": channel, "to": recipient, "subject": subject, "body": body, "requires_confirmation": True}

    async def _send(self, task: dict[str, Any]) -> dict[str, Any]:
        channel = str(task.get("channel", "email"))
        recipient = str(task.get("to", task.get("recipient", "")))
        subject = str(task.get("subject", ""))
        body = str(task.get("body", ""))
        log_agent_action(self.name, "send_blocked", {"channel": channel, "recipient": recipient})
        return {"status": "blocked", "reason": "send requires explicit UI confirmation", "channel": channel, "to": recipient, "subject": subject, "body": body}

    async def _list(self, task: dict[str, Any]) -> dict[str, Any]:
        channel = str(task.get("channel", "email"))
        if self._mcp:
            try:
                if channel == "email":
                    return await self.call_mcp("email", "list", {"max_results": int(task.get("max_results", 10))})
                return await self.call_mcp("messaging", "list_channels", {})
            except Exception as exc:
                self.log("list_error", error=str(exc))
        return {"status": "listed", "channel": channel, "items": []}
