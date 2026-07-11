"""Database repository helpers."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import Base


async def create(session: AsyncSession, obj: Base) -> Base:
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_by_id(session: AsyncSession, model: type[Base], obj_id: str) -> Base | None:
    result = await session.execute(select(model).where(model.id == obj_id))
    return result.scalar_one_or_none()


async def list_all(session: AsyncSession, model: type[Base], limit: int = 100) -> list[Base]:
    result = await session.execute(select(model).limit(limit))
    return list(result.scalars().all())


async def soft_delete(session: AsyncSession, model: type[Base], obj_id: str) -> bool:
    result = await session.execute(
        update(model).where(model.id == obj_id).values(updated_at=datetime.utcnow())
    )
    await session.commit()
    return result.rowcount > 0
