"""Memory and state management — short-term, episodic, long-term."""

from __future__ import annotations

import json
import logging
from typing import Any

from src.db.engine import async_session
from src.db.models import Session as SessionModel

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self) -> None:
        self._short_term: dict[str, list[dict[str, Any]]] = {}
        self._episodic: dict[str, list[dict[str, Any]]] = {}

    def add_short_term(self, session_id: str, message: dict[str, Any]) -> None:
        self._short_term.setdefault(session_id, []).append(message)
        if len(self._short_term[session_id]) > 200:
            self._short_term[session_id] = self._short_term[session_id][-200:]

    def get_short_term(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._short_term.get(session_id, []))

    def add_episodic(self, session_id: str, event: dict[str, Any]) -> None:
        self._episodic.setdefault(session_id, []).append(event)

    def get_episodic(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._episodic.get(session_id, []))

    async def persist_session(self, session_id: str, context: dict[str, Any]) -> None:
        async with async_session() as session:
            existing = await session.execute(
                SessionModel.__table__.select().where(SessionModel.id == session_id)
            )
            row = existing.fetchone()
            if row:
                await session.execute(
                    SessionModel.__table__.update()
                    .where(SessionModel.id == session_id)
                    .values(context=json.dumps(context), state=json.dumps(self._short_term.get(session_id, [])))
                )
            else:
                session.add(
                    SessionModel(
                        id=session_id,
                        context=json.dumps(context),
                        state=json.dumps(self._short_term.get(session_id, [])),
                    )
                )
            await session.commit()

    async def load_session(self, session_id: str) -> dict[str, Any] | None:
        async with async_session() as session:
            result = await session.execute(
                SessionModel.__table__.select().where(SessionModel.id == session_id)
            )
            row = result.fetchone()
            if not row:
                return None
            context = json.loads(row.context) if row.context else {}
            state = json.loads(row.state) if row.state else []
            self._short_term[session_id] = state
            return context
