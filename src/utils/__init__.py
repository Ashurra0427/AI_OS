"""Utility helpers."""

from __future__ import annotations

import asyncio
import hashlib
import time


def generate_id(prefix: str = "") -> str:
    raw = f"{prefix}{time.time()}{id(__import__('builtins').object())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def retry(attempts: int = 3, backoff: float = 1.0):
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(attempts):
                try:
                    return await fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    await asyncio.sleep(backoff * (2 ** attempt))
            raise last_exc
        return wrapper
    return decorator
