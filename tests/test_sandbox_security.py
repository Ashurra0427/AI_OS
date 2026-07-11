"""Tests for sandbox escape denial and security boundaries."""

from __future__ import annotations

import tempfile
import time

import pytest

from src.config.schemas import PermissionGrant
from src.mcp.permission_broker import PermissionBroker, PermissionDenied
from src.mcp.servers.shell import ShellMCPServer
from src.security.sandbox import SandboxedShell


@pytest.fixture
def broker():
    return PermissionBroker()


def test_sandbox_denies_path_traversal(broker):
    grant = PermissionGrant(
        agent="coder",
        server="filesystem",
        tools=["read_file"],
        scopes={"path": "/project"},
        granted_by="admin",
        granted_at=time.time(),
    )
    broker.grant(grant)
    with pytest.raises(PermissionDenied):
        broker.check("coder", "filesystem", "read_file", {"path": "/etc/passwd"})


def test_sandbox_denies_parent_escape(broker):
    grant = PermissionGrant(
        agent="coder",
        server="filesystem",
        tools=["read_file"],
        scopes={"path": "/project/src"},
        granted_by="admin",
        granted_at=time.time(),
    )
    broker.grant(grant)
    with pytest.raises(PermissionDenied):
        broker.check("coder", "filesystem", "read_file", {"path": "/project/src/../etc/passwd"})


def test_sandbox_shell_denies_network_by_default():
    with tempfile.TemporaryDirectory() as tmp:
        shell = SandboxedShell(allowed_dirs=[tmp], network_disabled=True)
        result = shell.run("curl -s http://example.com", cwd=tmp)
        assert result.get("blocked") is True or result["returncode"] != 0


def test_shell_mcp_denies_unsafe_command():
    import asyncio
    with tempfile.TemporaryDirectory() as tmp:
        srv = ShellMCPServer(allowed_dirs=[tmp])
        result = asyncio.run(srv.call_tool("run", {"command": "rm -rf /", "cwd": tmp}))
        assert result["returncode"] != 0
