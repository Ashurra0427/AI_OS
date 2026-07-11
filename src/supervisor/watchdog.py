"""Watchdog for health checks and crash recovery."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class HealthState:
    name: str
    healthy: bool = True
    last_check: float = field(default_factory=time.time)
    failure_count: int = 0
    max_failures: int = 3
    backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    current_backoff: float = 1.0

    def record_failure(self) -> None:
        self.healthy = False
        self.failure_count += 1
        self.current_backoff = min(
            self.backoff_seconds * (self.backoff_multiplier ** (self.failure_count - 1)),
            60.0,
        )

    def record_success(self) -> None:
        self.healthy = True
        self.failure_count = 0
        self.current_backoff = self.backoff_seconds
        self.last_check = time.time()


class Watchdog:
    def __init__(self) -> None:
        self._checks: dict[str, HealthState] = {}

    def register(self, name: str, max_failures: int = 3) -> None:
        self._checks[name] = HealthState(name=name, max_failures=max_failures)

    def check(self, name: str, check_fn) -> bool:
        state = self._checks.setdefault(name, HealthState(name=name))
        try:
            ok = bool(check_fn())
            if ok:
                state.record_success()
            else:
                state.record_failure()
            return ok
        except Exception:
            state.record_failure()
            return False

    @property
    def degraded_services(self) -> list[str]:
        return [name for name, st in self._checks.items() if not st.healthy]
