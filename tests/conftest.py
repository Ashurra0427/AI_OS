"""Shared pytest fixtures."""

from __future__ import annotations

import asyncio
import platform

import pytest

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
def sample_permission_grant():
    import time

    from src.config.schemas import PermissionGrant
    return PermissionGrant(
        agent="test_agent",
        server="filesystem",
        tools=["read_file", "list_directory"],
        scopes={"path": str(__import__('pathlib').Path.cwd())},
        granted_by="admin",
        granted_at=time.time(),
    )
