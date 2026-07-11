"""Init/supervisor for JARVIS services."""

from __future__ import annotations

import asyncio
import signal
import sys
from collections.abc import Callable

from src.config.settings import settings
from src.jarvis_logging.setup import setup_logging

setup_logging(settings.log_level)


class Supervisor:
    def __init__(self) -> None:
        self._services: list[Callable] = []
        self._tasks: list[asyncio.Task] = []
        self._shutdown = False

    def register(self, service_factory: Callable) -> None:
        self._services.append(service_factory)

    async def _run_service(self, factory: Callable) -> None:
        while not self._shutdown:
            try:
                svc = factory()
                if asyncio.iscoroutine(svc):
                    await svc
                else:
                    svc()
            except Exception as exc:
                import structlog
                log = structlog.get_logger()
                log.error("service_crashed", factory=factory.__name__, error=str(exc))
                await asyncio.sleep(1)

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        if sys.platform != "win32":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
        else:
            def _win_handler(signum, frame):
                asyncio.get_event_loop().call_soon_threadsafe(
                    lambda: asyncio.create_task(self.shutdown())
                )
            signal.signal(signal.SIGINT, _win_handler)
            if hasattr(signal, "SIGBREAK"):
                signal.signal(signal.SIGBREAK, _win_handler)
        for factory in self._services:
            task = asyncio.create_task(self._run_service(factory))
            self._tasks.append(task)
        if self._tasks:
            await asyncio.gather(*self._tasks)

    async def shutdown(self) -> None:
        self._shutdown = True
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
