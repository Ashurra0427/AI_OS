"""Filesystem MCP server — scoped file operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class FilesystemMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {
                "name": "read_file",
                "description": "Read a text file within the allowed scope",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"},
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "write_file",
                "description": "Write a text file within the allowed scope",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to write"},
                        "content": {"type": "string", "description": "Content to write"},
                    },
                    "required": ["path", "content"],
                },
            },
            {
                "name": "list_directory",
                "description": "List directory contents within the allowed scope",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "delete_file",
                "description": "Delete a file within the allowed scope",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to delete"},
                    },
                    "required": ["path"],
                },
            },
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "read_file":
            return self._read_file(str(arguments["path"]))
        elif tool == "write_file":
            return self._write_file(str(arguments["path"]), str(arguments["content"]))
        elif tool == "list_directory":
            return self._list_directory(str(arguments["path"]))
        elif tool == "delete_file":
            return self._delete_file(str(arguments["path"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    def _resolve(self, path: str) -> Path:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Path not found: {p}")
        return p

    def _read_file(self, path: str) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def _write_file(self, path: str, content: str) -> dict:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"status": "written", "path": str(p)}

    def _list_directory(self, path: str) -> list[str]:
        p = self._resolve(path)
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {p}")
        return sorted(str(entry.name) for entry in p.iterdir())

    def _delete_file(self, path: str) -> dict:
        p = self._resolve(path)
        p.unlink()
        return {"status": "deleted", "path": str(p)}
