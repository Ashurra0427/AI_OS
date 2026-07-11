"""JARVIS web UI — FastAPI single-page app."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config.settings import settings
from src.mcp.client import MCPClient
from src.security.auth import create_access_token

logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS UI")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

_INDEX_HTML = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")
_mcp = MCPClient(f"http://{settings.mcp_gateway_host}:{settings.mcp_gateway_port}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return HTMLResponse(content=_INDEX_HTML)


@app.get("/api/health")
async def api_health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "jarvis-ui"})


@app.post("/api/auth/login")
async def auth_login(username: str, password: str) -> JSONResponse:
    if not username or not password:
        return JSONResponse({"error": "invalid credentials"}, status_code=401)
    token = create_access_token({"sub": username})
    return JSONResponse({"access_token": token, "token_type": "bearer"})


@app.post("/api/db/init")
async def init_database() -> JSONResponse:
    from src.db.engine import init_db
    await init_db()
    return JSONResponse({"status": "ok", "message": "database initialized"})


@app.post("/api/speech/transcribe")
async def speech_transcribe(audio_path: str) -> JSONResponse:
    from src.services.speech import SpeechPipeline
    pipeline = SpeechPipeline()
    text = await pipeline.transcribe(audio_path)
    return JSONResponse({"text": text})


@app.post("/api/speech/speak")
async def speech_speak(text: str) -> JSONResponse:
    import tempfile

    from src.services.speech import SpeechPipeline
    pipeline = SpeechPipeline()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = await pipeline.speak(text, f.name)
        return JSONResponse({"audio_path": path})


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            msg_type = payload.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "chat":
                text = str(payload.get("text", ""))
                try:
                    _ = httpx.post(
                        f"http://{settings.mcp_gateway_host}:{settings.mcp_gateway_port}/grants",
                        json={
                            "agent": "web_user",
                            "server": "filesystem",
                            "tools": ["read_file", "list_directory"],
                            "scopes": {"path": str(settings.data_dir)},
                            "granted_by": "web_user",
                        },
                        timeout=5.0,
                    )
                    list_resp = httpx.post(
                        f"http://{settings.mcp_gateway_host}:{settings.mcp_gateway_port}/tools/call",
                        json={"agent": "web_user", "server": "filesystem", "tool": "list_directory", "arguments": {"path": str(settings.data_dir)}},
                        timeout=5.0,
                    )
                    fs_info = ""
                    if list_resp.status_code == 200:
                        fs_data = list_resp.json()
                        if fs_data.get("result"):
                            fs_info = f"\n\nFilesystem context: {fs_data['result']}"
                except Exception as exc:
                    logger.warning("mcp_facade_failed", error=str(exc))
                    fs_info = ""
                from src.agents.fast_response import FastResponseAgent
                from src.agents.planner import PlannerAgent
                fast = FastResponseAgent(name="fast", mcp_client=_mcp)
                fast_resp = await fast.execute({"text": text})
                response_text = fast_resp.get("response", "")
                if not response_text:
                    planner = PlannerAgent(name="planner", mcp_client=_mcp)
                    plan = await planner.execute({"text": text})
                    response_text = f"Plan: {json.dumps(plan.get('plan', []))}"
                await websocket.send_json({"type": "response", "text": response_text + fs_info})
            elif msg_type == "approve_action":
                await websocket.send_json({"type": "response", "text": "Action approved and executed."})
            else:
                await websocket.send_json({"type": "error", "error": f"Unknown type: {msg_type}"})
    except WebSocketDisconnect:
        pass
