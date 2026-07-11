"""JARVIS-AI-OS main entry point."""

from __future__ import annotations

import asyncio
import sys

import uvicorn

from src.config.settings import settings
from src.jarvis_logging.setup import setup_logging
from src.supervisor.init import Supervisor
from src.ui.web import app as ui_app


def _run_ui() -> None:
    uvicorn.run(ui_app, host=settings.mcp_gateway_host, port=settings.mcp_gateway_port + 1, log_level="warning")


def main() -> int:
    setup_logging(settings.log_level)
    supervisor = Supervisor()
    supervisor.register(_run_ui)
    return asyncio.run(supervisor.start())


if __name__ == "__main__":
    sys.exit(main() or 0)
