"""Auth helpers — JWT tokens and password hashing."""

from __future__ import annotations

import datetime
from typing import Any

from src.config.settings import settings


def create_access_token(data: dict[str, Any], expires_delta: datetime.timedelta | None = None) -> str:
    import jwt
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + (expires_delta or datetime.timedelta(minutes=settings.jwt_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    import jwt
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
