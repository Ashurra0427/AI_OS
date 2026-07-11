"""Tests for Filesystem MCP server."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.mcp.servers.filesystem import FilesystemMCPServer


@pytest.mark.asyncio
async def test_filesystem_read_write() -> None:
    server = FilesystemMCPServer()
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "test.txt")
        write_res = await server.call_tool("write_file", {"path": file_path, "content": "hello"})
        assert write_res["status"] == "written"
        read_res = await server.call_tool("read_file", {"path": file_path})
        assert read_res == "hello"


@pytest.mark.asyncio
async def test_filesystem_list() -> None:
    server = FilesystemMCPServer()
    with tempfile.TemporaryDirectory() as tmp:
        res = await server.call_tool("list_directory", {"path": tmp})
        assert isinstance(res, list)
