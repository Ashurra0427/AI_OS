# JARVIS-AI-OS

AI-native operating system layer with MCP tool integration, hybrid inference, and sandboxed agents.

## Quick Start

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Architecture

- **Phase 0**: App skeleton (config, logging, eventbus, init/supervisor)
- **Phase 1**: MCP gateway + permission broker + filesystem MCP
- **Phase 2**: Search/research MCP server
- **Phase 3**: LLM hybrid switch + MoE router + RAG
- **Phase 4**: STT/TTS with offline fallback
- **Phase 5**: VLM + SAM
- **Phase 6**: Planner, Coding, Research, Analysis agents
- **Phase 7**: LAM + Vision/Automation Agent
- **Phase 8**: Communication Agent
- **Phase 9**: Fast-Response Agent (SLM)

## Docs

- `MODEL_CLASSES.md` — model class reference
- `MCP_SERVERS.md` — MCP server registry
