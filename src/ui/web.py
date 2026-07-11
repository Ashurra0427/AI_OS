"""JARVIS web UI — FastAPI single-page app."""

from __future__ import annotations

import json
import logging
import tempfile
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
async def speech_transcribe(request: Request) -> JSONResponse:
    content_type = request.headers.get('content-type', '')
    audio_path = None
    if 'multipart/form-data' in content_type:
        form = await request.form()
        upload = form.get('file')
        if upload:
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                f.write(await upload.read())
                audio_path = f.name
    else:
        body = await request.body()
        if body:
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                f.write(body)
                audio_path = f.name
    if not audio_path:
        return JSONResponse({"text": ""})
    try:
        from src.services.speech import SpeechPipeline
        pipeline = SpeechPipeline()
        text = await pipeline.transcribe(audio_path)
        return JSONResponse({"text": text})
    except Exception as exc:
        logger.error("speech_transcribe_failed", error=str(exc))
        return JSONResponse({"text": ""})
    finally:
        try:
            Path(audio_path).unlink(missing_ok=True)
        except Exception:
            pass


@app.post("/api/speech/speak")
async def speech_speak(text: str) -> JSONResponse:
    try:
        from src.services.speech import SpeechPipeline
        pipeline = SpeechPipeline()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = await pipeline.speak(text, f.name)
            return JSONResponse({"audio_path": path})
    except Exception as exc:
        logger.error("speech_speak_failed", error=str(exc))
        return JSONResponse({"audio_path": ""})


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
                agent_used = "fast"
                tools_used = []
                response_text = ""
                try:
                    from src.agents.fast_response import FastResponseAgent
                    from src.agents.planner import PlannerAgent
                    from src.agents.research import ResearchAgent
                    fast = FastResponseAgent(name="fast", mcp_client=_mcp)
                    fast_resp = await fast.execute({"text": text})
                    response_text = fast_resp.get("response", "")
                    if response_text and not response_text.startswith("["):
                        agent_used = "fast"
                    else:
                        planner = PlannerAgent(name="planner", mcp_client=_mcp)
                        plan = await planner.execute({"text": text})
                        agent_used = "planner"
                        steps = plan.get("plan", [])
                        response_text = f"Delegated to {len(steps)} steps: " + ", ".join(f"{s['agent']}: {s['action']}" for s in steps)
                        tools_used = ["MoERouter", "Planner"]
                        if "search" in text.lower() or "find" in text.lower() or "look up" in text.lower():
                            try:
                                research = ResearchAgent(name="research", mcp_client=_mcp)
                                research_resp = await research.execute({"query": text})
                                results = research_resp.get("results", [])
                                if results:
                                    response_text += f"\n\nFound {len(results)} results:\n"
                                    for i, r in enumerate(results[:3], 1):
                                        response_text += f"{i}. {r.get('title', '')}\n   {r.get('url', '')}\n   {r.get('snippet', '')}\n"
                                    tools_used.append("web_search")
                            except Exception:
                                pass
                except Exception as exc:
                    logger.warning("agent_pipeline_failed", error=str(exc))
                    response_text = f"Agent pipeline error: {exc}"
                    agent_used = "error"
                await websocket.send_json({
                    "type": "response",
                    "text": response_text,
                    "agent": agent_used,
                    "tools": tools_used,
                })
            elif msg_type == "approve_action":
                await websocket.send_json({"type": "response", "text": "Action approved and executed."})
            else:
                await websocket.send_json({"type": "error", "error": f"Unknown type: {msg_type}"})
    except WebSocketDisconnect:
        pass
