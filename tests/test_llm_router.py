"""Tests for LLM router and MoE."""

from __future__ import annotations

import pytest

from src.models.router import MoERouter


@pytest.mark.asyncio
async def test_router_prefers_local_for_trivial() -> None:
    router = MoERouter()
    router.add_local_rule("ping")
    result = await router.route({"text": "ping"})
    assert result["target"] == "local"


@pytest.mark.asyncio
async def test_router_prefers_cloud_for_complex() -> None:
    router = MoERouter()
    result = await router.route({"text": "explain quantum computing"})
    assert result["target"] == "cloud"
