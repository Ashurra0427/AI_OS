"""JARVIS web UI — FastAPI + Jinja2 templates."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="JARVIS UI")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def api_health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "jarvis-ui"})


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
                await websocket.send_json({
                    "type": "response",
                    "text": f"Echo: {payload.get('text', '')}",
                })
            else:
                await websocket.send_json({"type": "error", "error": f"Unknown type: {msg_type}"})
    except WebSocketDisconnect:
        pass
