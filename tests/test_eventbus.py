"""Tests for EventBus."""

from __future__ import annotations

import asyncio

import pytest


@pytest.mark.asyncio
async def test_eventbus_pub_sub() -> None:
    from src.eventbus.bus import EventBus
    addr = "inproc://test-bus"
    bus = EventBus(addr, addr)
    received: list = []
    async def handler(data):
        received.append(data)
    bus.subscribe("test", handler)
    await bus.start()
    await asyncio.sleep(2.0)
    await bus.publish("test", {"msg": "hello"})
    await asyncio.sleep(2.0)
    assert len(received) == 1
    assert received[0]["msg"] == "hello"
    await bus.stop()
