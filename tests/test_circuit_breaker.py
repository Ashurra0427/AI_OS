"""Tests for circuit breaker and retry utilities."""

from __future__ import annotations

import pytest

from src.utils.circuit_breaker import CircuitBreaker, retry_with_backoff


@pytest.mark.asyncio
async def test_circuit_breaker_closes_on_success() -> None:
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    async def _return_42():
        return 42
    result = await cb.call(_return_42)
    assert result == 42
    assert cb.state == "closed"


@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures() -> None:
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

    async def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await cb.call(fail)
    with pytest.raises(RuntimeError):
        await cb.call(fail)
    assert cb.state == "open"


@pytest.mark.asyncio
async def test_circuit_breaker_rejects_when_open() -> None:
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10)

    async def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await cb.call(fail)
    assert cb.state == "open"
    with pytest.raises(RuntimeError, match="Circuit breaker is open"):
        await cb.call(lambda: 42)


@pytest.mark.asyncio
async def test_retry_with_backoff() -> None:
    calls = []

    async def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("fail")
        return "ok"

    result = await retry_with_backoff(flaky, attempts=3, backoff=0.01)
    assert result == "ok"
    assert len(calls) == 3
