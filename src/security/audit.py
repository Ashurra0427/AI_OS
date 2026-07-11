"""Audit logging for security events."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger()


def log_permission_check(agent: str, server: str, tool: str, granted: bool) -> None:
    logger.info(
        "permission_check",
        agent=agent,
        server=server,
        tool=tool,
        granted=granted,
    )


def log_tool_call(agent: str, server: str, tool: str, arguments: dict, result: Any, error: str | None) -> None:
    logger.info(
        "tool_call",
        agent=agent,
        server=server,
        tool=tool,
        arguments=arguments,
        result=result,
        error=error,
    )


def log_agent_action(agent: str, action: str, details: dict) -> None:
    logger.info("agent_action", agent=agent, action=action, event_type=action, **details)
