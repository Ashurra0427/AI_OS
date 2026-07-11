"""Tests for PermissionBroker."""

from __future__ import annotations

import pytest

from src.mcp.permission_broker import PermissionBroker, PermissionDenied


def test_grant_and_check(sample_permission_grant) -> None:
    broker = PermissionBroker()
    broker.grant(sample_permission_grant)
    broker.check("test_agent", "filesystem", "read_file", {"path": str(__import__('pathlib').Path.cwd())})


def test_check_denies_no_grant() -> None:
    broker = PermissionBroker()
    with pytest.raises(PermissionDenied):
        broker.check("test_agent", "filesystem", "read_file", {"path": "/tmp"})


def test_check_denies_wrong_tool(sample_permission_grant) -> None:
    broker = PermissionBroker()
    broker.grant(sample_permission_grant)
    with pytest.raises(PermissionDenied):
        broker.check("test_agent", "filesystem", "delete_file", {"path": "/tmp"})
