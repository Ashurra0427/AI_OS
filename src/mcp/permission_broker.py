"""Permission broker — enforces per-agent MCP scopes."""

from __future__ import annotations

import logging
from typing import Any

from src.config.schemas import PermissionGrant

logger = logging.getLogger(__name__)


class PermissionDenied(Exception):
    pass


class PermissionBroker:
    def __init__(self) -> None:
        self._grants: dict[str, PermissionGrant] = {}

    def grant(self, grant: PermissionGrant) -> None:
        key = f"{grant.agent}:{grant.server}"
        self._grants[key] = grant
        logger.info("permission_granted", agent=grant.agent, server=grant.server)

    def revoke(self, agent: str, server: str) -> None:
        key = f"{agent}:{server}"
        self._grants.pop(key, None)
        logger.info("permission_revoked", agent=agent, server=server)

    def check(self, agent: str, server: str, tool: str, arguments: dict[str, Any]) -> None:
        key = f"{agent}:{server}"
        grant = self._grants.get(key)
        if grant is None:
            raise PermissionDenied(f"No permission grant for {agent} on {server}")
        if tool not in grant.tools:
            raise PermissionDenied(f"Tool {tool} not in granted tools for {agent}")
        scope_violations = self._check_scopes(grant.scopes, arguments)
        if scope_violations:
            raise PermissionDenied(f"Scope violations: {scope_violations}")
        logger.debug(
            "permission_check_passed",
            agent=agent,
            server=server,
            tool=tool,
        )

    def _check_scopes(self, scopes: dict[str, str], arguments: dict[str, Any]) -> list[str]:
        violations = []
        path_arg = arguments.get("path") or arguments.get("file_path") or arguments.get("filename")
        if path_arg and "path" in scopes:
            import os
            allowed = os.path.normpath(scopes["path"].rstrip("/"))
            target = os.path.normpath(str(path_arg).rstrip("/"))
            if allowed != "*" and not (target == allowed or target.startswith(allowed + os.sep)):
                violations.append(f"path {path_arg} outside scope {scopes['path']}")
        return violations

    def get_agent_grants(self, agent: str) -> list[PermissionGrant]:
        return [g for k, g in self._grants.items() if k.startswith(f"{agent}:")]
