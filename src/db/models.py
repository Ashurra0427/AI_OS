"""SQLAlchemy ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, MappedColumn, relationship

from src.db.engine import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = MappedColumn(String(100), unique=True, nullable=False)
    type: Mapped[str] = MappedColumn(String(50), nullable=False)
    status: Mapped[str] = MappedColumn(String(20), default="idle")
    config: Mapped[str | None] = MappedColumn(Text)
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks: Mapped[list[AgentTask]] = relationship("AgentTask", back_populates="agent")


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    agent_id: Mapped[str] = MappedColumn(String(36), ForeignKey("agents.id"), nullable=False)
    action: Mapped[str] = MappedColumn(String(100), nullable=False)
    parameters: Mapped[str | None] = MappedColumn(Text)
    status: Mapped[str] = MappedColumn(String(20), default="pending")
    result: Mapped[str | None] = MappedColumn(Text)
    error: Mapped[str | None] = MappedColumn(Text)
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = MappedColumn(DateTime)

    agent: Mapped[Agent] = relationship("Agent", back_populates="tasks")


class PermissionGrantDB(Base):
    __tablename__ = "permission_grants"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    agent: Mapped[str] = MappedColumn(String(100), nullable=False)
    server: Mapped[str] = MappedColumn(String(100), nullable=False)
    tools: Mapped[str] = MappedColumn(Text, nullable=False)
    scopes: Mapped[str] = MappedColumn(Text, nullable=False)
    granted_by: Mapped[str] = MappedColumn(String(100), nullable=False)
    granted_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)
    revoked: Mapped[bool] = MappedColumn(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    agent: Mapped[str] = MappedColumn(String(100), nullable=False)
    action: Mapped[str] = MappedColumn(String(100), nullable=False)
    details: Mapped[str | None] = MappedColumn(Text)
    level: Mapped[str] = MappedColumn(String(20), default="info")
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    source: Mapped[str | None] = MappedColumn(String(255))
    content: Mapped[str] = MappedColumn(Text, nullable=False)
    metadata_: Mapped[str | None] = MappedColumn("metadata", Text)
    embedding: Mapped[str | None] = MappedColumn(Text)
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = MappedColumn(String(100))
    context: Mapped[str | None] = MappedColumn(Text)
    state: Mapped[str | None] = MappedColumn(Text)
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Secret(Base):
    __tablename__ = "secrets"

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=_uuid)
    key: Mapped[str] = MappedColumn(String(255), unique=True, nullable=False)
    value_encrypted: Mapped[str] = MappedColumn("value", Text, nullable=False)
    provider: Mapped[str | None] = MappedColumn(String(100))
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)