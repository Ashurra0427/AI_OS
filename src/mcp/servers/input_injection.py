"""Input injection MCP server — requires explicit per-session grant."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class InputInjectionMCPServer:
    def __init__(self) -> None:
        self._granted = False
        self.tools = [
            {
                "name": "click",
                "description": "Click at screen coordinates",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"},
                    },
                    "required": ["x", "y"],
                },
            },
            {
                "name": "type",
                "description": "Type text at current focus",
                "inputSchema": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            },
            {
                "name": "hotkey",
                "description": "Press a hotkey combination",
                "inputSchema": {
                    "type": "object",
                    "properties": {"keys": {"type": "array", "items": {"type": "string"}}},
                    "required": ["keys"],
                },
            },
        ]

    def grant(self) -> None:
        self._granted = True
        logger.warning("input_injection_granted")

    def revoke(self) -> None:
        self._granted = False
        logger.info("input_injection_revoked")

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if not self._granted:
            raise PermissionError("Input injection not granted for this session")
        if tool == "click":
            return self._click(int(arguments["x"]), int(arguments["y"]), str(arguments.get("button", "left")))
        elif tool == "type":
            return self._type(str(arguments["text"]))
        elif tool == "hotkey":
            return self._hotkey(list(arguments["keys"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    def _click(self, x: int, y: int, button: str) -> dict[str, Any]:
        logger.info("input_click", x=x, y=y, button=button)
        return {"status": "clicked", "x": x, "y": y, "button": button}

    def _type(self, text: str) -> dict[str, Any]:
        logger.info("input_type", text_length=len(text))
        return {"status": "typed", "text": text}

    def _hotkey(self, keys: list[str]) -> dict[str, Any]:
        logger.info("input_hotkey", keys=keys)
        return {"status": "hotkey_pressed", "keys": keys}
