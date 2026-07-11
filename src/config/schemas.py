"""Shared Pydantic schemas for JARVIS."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str
    server: str
    tool: str
    arguments: dict[str, object]
    result: object | None = None
    error: str | None = None
    status: str = "pending"


class AgentMessage(BaseModel):
    id: str
    agent: str
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    parent_id: str | None = None


class PermissionGrant(BaseModel):
    agent: str
    server: str
    tools: list[str]
    scopes: dict[str, str]
    granted_by: str
    granted_at: float
