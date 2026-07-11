"""Tests for VLM, SAM, LAM, MCP servers, memory, and auth."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.mcp.servers.browser import BrowserAutomationMCPServer
from src.mcp.servers.calendar import CalendarMCPServer
from src.mcp.servers.email import EmailMCPServer
from src.mcp.servers.input_injection import InputInjectionMCPServer
from src.mcp.servers.messaging import MessagingMCPServer
from src.mcp.servers.shell import ShellMCPServer
from src.memory.store import MemoryStore
from src.models.lam import LAM
from src.models.sam import SAM
from src.models.vlm import VLM
from src.security.auth import create_access_token, decode_access_token


class MockMCP:
    async def call_tool(self, server, tool, arguments):
        return {"mock": True}


@pytest.mark.asyncio
async def test_vlm_ocr_missing_image() -> None:
    vlm = VLM()
    result = await vlm.ocr("/tmp/nonexistent_image_12345.png")
    assert "[VLM unavailable]" in result


@pytest.mark.asyncio
async def test_vlm_analyze_real_image() -> None:
    vlm = VLM()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        from PIL import Image
        Image.new("RGB", (10, 10), color="red").save(f.name)
        try:
            result = await vlm.analyze(f.name, "Describe this image.")
            assert "text" in result
        finally:
            import contextlib
            with contextlib.suppress(PermissionError):
                os.unlink(f.name)


def test_sam_segment_missing() -> None:
    sam = SAM()
    result = sam.segment("C:\\nonexistent\\path\\image.png")
    assert result == []


def test_sam_segment_real_image() -> None:
    sam = SAM()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        from PIL import Image
        Image.new("RGB", (10, 10), color="blue").save(f.name)
        img = Image.open(f.name)
        img.close()
        result = sam.segment(f.name)
        assert len(result) >= 1
        import contextlib
        with contextlib.suppress(PermissionError):
            os.unlink(f.name)


@pytest.mark.asyncio
async def test_lam_execute() -> None:
    lam = LAM(mcp_client=MockMCP())
    result = await lam.execute("click", {"x": 100, "y": 200, "button": "left"})
    assert result.get("mock") is True
    assert len(lam.history) == 1


@pytest.mark.asyncio
async def test_lam_unsupported_action() -> None:
    lam = LAM(mcp_client=MockMCP())
    with pytest.raises(ValueError, match="Unsupported LAM action"):
        await lam.execute("fly", {})


@pytest.mark.asyncio
async def test_browser_mcp_navigate() -> None:
    srv = BrowserAutomationMCPServer()
    result = await srv.call_tool("navigate", {"url": "https://example.com"})
    assert result["status"] == "navigated"


@pytest.mark.asyncio
async def test_email_mcp_draft_and_send() -> None:
    srv = EmailMCPServer()
    draft = await srv.call_tool("draft", {"to": "a@b.com", "subject": "s", "body": "b"})
    assert draft["status"] == "drafted"
    assert draft.get("requires_confirmation") is True


@pytest.mark.asyncio
async def test_messaging_mcp_list_channels() -> None:
    srv = MessagingMCPServer()
    result = await srv.call_tool("list_channels", {})
    assert len(result) == 4


@pytest.mark.asyncio
async def test_calendar_mcp_create_blocked() -> None:
    srv = CalendarMCPServer()
    result = await srv.call_tool("create_event", {"title": "t", "start": "2025-01-01", "end": "2025-01-02"})
    assert result["status"] == "blocked"


def test_input_injection_grant_required() -> None:
    srv = InputInjectionMCPServer()
    with pytest.raises(PermissionError):
        import asyncio
        asyncio.run(srv.call_tool("click", {"x": 1, "y": 2}))


@pytest.mark.asyncio
async def test_input_injection_after_grant() -> None:
    srv = InputInjectionMCPServer()
    srv.grant()
    result = await srv.call_tool("click", {"x": 1, "y": 2})
    assert result["status"] == "clicked"


@pytest.mark.asyncio
async def test_shell_mcp_run() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        srv = ShellMCPServer(allowed_dirs=[tmp])
        result = await srv.call_tool("run", {"command": "python --version", "cwd": tmp})
        assert result["returncode"] == 0


def test_memory_store() -> None:
    store = MemoryStore()
    store.add_short_term("s1", {"role": "user", "content": "hi"})
    assert len(store.get_short_term("s1")) == 1
    store.add_episodic("s1", {"event": "start"})
    assert len(store.get_episodic("s1")) == 1


def test_auth_token_roundtrip() -> None:
    token = create_access_token({"sub": "user1"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user1"