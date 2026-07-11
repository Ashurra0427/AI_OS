"""Tests for Email MCP server — IMAP/SMTP universal backend."""

from __future__ import annotations

import pytest

from src.config.settings import settings
from src.mcp.servers.email import EmailMCPServer


@pytest.mark.asyncio
async def test_email_draft_requires_confirmation() -> None:
    srv = EmailMCPServer()
    result = await srv.call_tool("draft", {"to": "user@example.com", "subject": "hi", "body": "hello"})
    assert result["status"] == "drafted"
    assert result.get("requires_confirmation") is True


@pytest.mark.asyncio
async def test_email_send_without_key() -> None:
    srv = EmailMCPServer()
    original = settings.email_api_key
    settings.email_api_key = None
    try:
        with pytest.raises(RuntimeError, match="email_api_key not configured"):
            await srv.call_tool("send", {"to": "user@example.com", "subject": "hi", "body": "hello"})
    finally:
        settings.email_api_key = original


@pytest.mark.asyncio
async def test_email_list_without_key() -> None:
    srv = EmailMCPServer()
    original = settings.email_api_key
    settings.email_api_key = None
    try:
        with pytest.raises(RuntimeError, match="email_api_key not configured"):
            await srv.call_tool("list", {"max_results": 5})
    finally:
        settings.email_api_key = original


def test_imap_host_detection() -> None:
    assert EmailMCPServer._imap_host_for("user@gmail.com") == "imap.gmail.com"
    assert EmailMCPServer._imap_host_for("user@outlook.com") == "outlook.office365.com"
    assert EmailMCPServer._imap_host_for("user@yahoo.com") == "imap.mail.yahoo.com"
    assert EmailMCPServer._imap_host_for("user@custom.com") == "imap.custom.com"


def test_smtp_host_detection() -> None:
    assert EmailMCPServer._smtp_host_for("user@gmail.com") == "smtp.gmail.com"
    assert EmailMCPServer._smtp_host_for("user@outlook.com") == "smtp.office365.com"
    assert EmailMCPServer._smtp_host_for("user@yahoo.com") == "smtp.mail.yahoo.com"
    assert EmailMCPServer._smtp_host_for("user@custom.com") == "smtp.custom.com"
