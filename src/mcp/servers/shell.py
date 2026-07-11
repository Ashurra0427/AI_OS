"""Shell/terminal MCP server — runs in a disposable sandbox per task."""

from __future__ import annotations

import logging
from typing import Any

from src.security.sandbox import SandboxedShell

logger = logging.getLogger(__name__)


class ShellMCPServer:
    def __init__(self, allowed_dirs: list[str] | None = None) -> None:
        self._allowed_dirs = allowed_dirs or ["/project"]
        self._sandbox = SandboxedShell(allowed_dirs=self._allowed_dirs, network_disabled=True)
        self.tools = [
            {"name": "run", "description": "Run a shell command in the sandbox", "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}, "cwd": {"type": "string"}}, "required": ["command"]}},
            {"name": "write_file", "description": "Write a file in the sandbox", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
            {"name": "read_file", "description": "Read a file in the sandbox", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "run":
            return self._sandbox.run(str(arguments["command"]), cwd=arguments.get("cwd"))
        elif tool == "write_file":
            return self._sandbox._write_file(str(arguments["path"]), str(arguments["content"]))
        elif tool == "read_file":
            return self._sandbox._read_file(str(arguments["path"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")
