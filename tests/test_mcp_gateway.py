"""Tests for MCP gateway."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.mcp.gateway import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_grant_then_call() -> None:
    grant_resp = client.post("/grants", json={
        "agent": "test_agent",
        "server": "filesystem",
        "tools": ["read_file", "list_directory"],
        "scopes": {"path": str(__import__('pathlib').Path.cwd())},
        "granted_by": "admin",
    })
    assert grant_resp.status_code == 200
    call_resp = client.post("/tools/call", json={
        "agent": "test_agent",
        "server": "filesystem",
        "tool": "list_directory",
        "arguments": {"path": str(__import__('pathlib').Path.cwd())},
    })
    assert call_resp.status_code == 200


def test_call_denied_without_grant() -> None:
    resp = client.post("/tools/call", json={
        "agent": "no_grant_agent",
        "server": "filesystem",
        "tool": "read_file",
        "arguments": {"path": str(__import__('pathlib').Path.cwd())},
    })
    assert resp.status_code == 403
