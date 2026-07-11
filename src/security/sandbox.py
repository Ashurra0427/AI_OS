"""Sandbox utilities for agent execution."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class SandboxedShell:
    _DENY_PATTERNS = [
        re.compile(r"rm\s+-rf\s+/"),
        re.compile(r"rm\s+-rf\s+\\"),
        re.compile(r"del\s+/[sS]"),
        re.compile(r"format\s+[cCdDeEfF]:?"),
        re.compile(r"shutdown"),
        re.compile(r"reboot"),
        re.compile(r"curl\s+"),
        re.compile(r"wget\s+"),
        re.compile(r"nc\s+-"),
        re.compile(r"netcat\s+-"),
    ]

    def __init__(self, allowed_dirs: list[str], network_disabled: bool = True) -> None:
        self._allowed_dirs = [Path(d).resolve() for d in allowed_dirs]
        self._network_disabled = network_disabled

    def run(self, command: str, cwd: str | None = None) -> dict[str, Any]:
        for pattern in self._DENY_PATTERNS:
            if pattern.search(command):
                return {"stdout": "", "stderr": f"command blocked by sandbox policy: {pattern.pattern}", "returncode": -1, "blocked": True}
        with tempfile.TemporaryDirectory() as tmp:
            resolved_cwd = Path(cwd or tmp).resolve()
            if not any(
                str(resolved_cwd).startswith(str(d)) for d in self._allowed_dirs
            ):
                return {"stdout": "", "stderr": "cwd outside allowed scope", "returncode": -1}
            env = os.environ.copy()
            if self._network_disabled:
                env["no_proxy"] = "*"
                env["NO_PROXY"] = "*"
            try:
                proc = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(resolved_cwd),
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=env,
                )
                return {
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "returncode": proc.returncode,
                }
            except subprocess.TimeoutExpired:
                return {"stdout": "", "stderr": "timeout", "returncode": -1}
            except Exception as exc:
                return {"stdout": "", "stderr": str(exc), "returncode": -1}

    def _write_file(self, path: str, content: str) -> dict[str, Any]:
        p = Path(path).expanduser()
        if not any(str(p.resolve()).startswith(str(d)) for d in self._allowed_dirs):
            return {"status": "error", "error": "path outside allowed scope"}
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"status": "written", "path": str(p)}

    def _read_file(self, path: str) -> str:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Path not found: {p}")
        return p.read_text(encoding="utf-8")
