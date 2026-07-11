"""MCP Gateway — FastAPI service exposing MCP tool calls."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config.settings import settings
from src.jarvis_logging.setup import setup_logging
from src.mcp.permission_broker import PermissionBroker, PermissionDenied

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS MCP Gateway")
broker = PermissionBroker()


class ToolCallRequest(BaseModel):
    agent: str
    server: str
    tool: str
    arguments: dict[str, Any]


class GrantRequest(BaseModel):
    agent: str
    server: str
    tools: list[str]
    scopes: dict[str, str]
    granted_by: str


_SERVER_REGISTRY: dict[str, Any] = {}


def _get_server(name: str) -> Any:
    if name in _SERVER_REGISTRY:
        return _SERVER_REGISTRY[name]
    if name == "filesystem":
        from src.mcp.servers.filesystem import FilesystemMCPServer
        _SERVER_REGISTRY[name] = FilesystemMCPServer()
    elif name == "search":
        from src.mcp.servers.search import SearchMCPServer
        _SERVER_REGISTRY[name] = SearchMCPServer()
    elif name == "browser":
        from src.mcp.servers.browser import BrowserAutomationMCPServer
        _SERVER_REGISTRY[name] = BrowserAutomationMCPServer()
    elif name == "input_injection":
        from src.mcp.servers.input_injection import InputInjectionMCPServer
        _SERVER_REGISTRY[name] = InputInjectionMCPServer()
    elif name == "email":
        from src.mcp.servers.email import EmailMCPServer
        _SERVER_REGISTRY[name] = EmailMCPServer()
    elif name == "messaging":
        from src.mcp.servers.messaging import MessagingMCPServer
        _SERVER_REGISTRY[name] = MessagingMCPServer()
    elif name == "calendar":
        from src.mcp.servers.calendar import CalendarMCPServer
        _SERVER_REGISTRY[name] = CalendarMCPServer()
    elif name == "shell":
        from src.mcp.servers.shell import ShellMCPServer
        _SERVER_REGISTRY[name] = ShellMCPServer(allowed_dirs=["/project"])
    else:
        raise HTTPException(status_code=400, detail=f"Unknown server: {name}")
    return _SERVER_REGISTRY[name]


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "mcp-gateway"}


@app.post("/grants")
async def create_grant(req: GrantRequest) -> dict:
    import time

    from src.config.schemas import PermissionGrant
    grant = PermissionGrant(
        agent=req.agent,
        server=req.server,
        tools=req.tools,
        scopes=req.scopes,
        granted_by=req.granted_by,
        granted_at=time.time(),
    )
    broker.grant(grant)
    return {"status": "granted"}


@app.post("/tools/call")
async def call_tool(req: ToolCallRequest) -> dict:
    try:
        broker.check(req.agent, req.server, req.tool, req.arguments)
    except PermissionDenied as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    server = _get_server(req.server)
    try:
        result = await server.call_tool(req.tool, req.arguments)
        return {"result": result, "error": None}
    except Exception as exc:
        logger.error("tool_call_failed", server=req.server, tool=req.tool, error=str(exc))
        return {"result": None, "error": str(exc)}


@app.get("/servers/{server}/tools")
async def list_tools(server: str) -> dict:
    srv = _get_server(server)
    return {"tools": srv.tools}
