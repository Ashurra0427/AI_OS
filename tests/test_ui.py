"""Tests for UI endpoints, auth, and wiring."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.ui.web import app

client = TestClient(app)


def test_ui_health() -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ui_index() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "JARVIS-AI-OS" in resp.text
    assert "agent-badge" in resp.text
    assert "tool-calls" in resp.text


def test_auth_login() -> None:
    resp = client.post("/api/auth/login?username=user&password=pass")
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_db_init() -> None:
    resp = client.post("/api/db/init")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ui_index() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "JARVIS-AI-OS" in resp.text


def test_auth_login() -> None:
    resp = client.post("/api/auth/login?username=user&password=pass")
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_db_init() -> None:
    resp = client.post("/api/db/init")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
