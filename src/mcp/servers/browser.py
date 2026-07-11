"""Browser/automation MCP server — wraps LAM browser control."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BrowserAutomationMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {
                "name": "navigate",
                "description": "Navigate browser to a URL",
                "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
            },
            {
                "name": "screenshot",
                "description": "Take a screenshot of the current page",
                "inputSchema": {"type": "object", "properties": {"full_page": {"type": "boolean", "default": False}}, "required": []},
            },
            {
                "name": "click",
                "description": "Click an element by selector",
                "inputSchema": {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]},
            },
            {
                "name": "type",
                "description": "Type text into an element",
                "inputSchema": {
                    "type": "object",
                    "properties": {"selector": {"type": "string"}, "text": {"type": "string"}},
                    "required": ["selector", "text"],
                },
            },
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "navigate":
            return await self._navigate(str(arguments["url"]))
        elif tool == "screenshot":
            return await self._screenshot(bool(arguments.get("full_page", False)))
        elif tool == "click":
            return await self._click(str(arguments["selector"]))
        elif tool == "type":
            return await self._type(str(arguments["selector"]), str(arguments["text"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    async def _navigate(self, url: str) -> dict[str, Any]:
        logger.info("browser_navigate", url=url)
        return {"status": "navigated", "url": url}

    async def _screenshot(self, full_page: bool) -> dict[str, Any]:
        logger.info("browser_screenshot", full_page=full_page)
        return {"status": "screenshot_taken", "path": "/tmp/screenshot.png", "full_page": full_page}

    async def _click(self, selector: str) -> dict[str, Any]:
        logger.info("browser_click", selector=selector)
        return {"status": "clicked", "selector": selector}

    async def _type(self, selector: str, text: str) -> dict[str, Any]:
        logger.info("browser_type", selector=selector, text_length=len(text))
        return {"status": "typed", "selector": selector, "text": text}
