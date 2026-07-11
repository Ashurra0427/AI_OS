"""Circuit breaker and retry utilities for external API calls."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "closed"

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("circuit_breaker_half_open")
            else:
                raise RuntimeError("Circuit breaker is open")
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("circuit_breaker_closed")
            return result
        except Exception as exc:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.warning("circuit_breaker_failure count=%d error=%s", self.failure_count, str(exc))
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error("circuit_breaker_opened")
            raise


async def retry_with_backoff(func: Callable, attempts: int = 3, backoff: float = 1.0) -> Any:
    last_exc = None
    for attempt in range(attempts):
        try:
            return await func()
        except Exception as exc:
            last_exc = exc
            logger.warning("retry attempt=%d error=%s", attempt + 1, str(exc))
            await asyncio.sleep(backoff * (2 ** attempt))
    raise last_exc
