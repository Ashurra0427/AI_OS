"""Tests for agents."""

from __future__ import annotations

import pytest

from src.agents.analysis import AnalysisAgent
from src.agents.coding import CodingAgent
from src.agents.communication import CommunicationAgent
from src.agents.fast_response import FastResponseAgent
from src.agents.planner import PlannerAgent
from src.agents.research import ResearchAgent
from src.agents.vision import VisionAutomationAgent


class MockMCP:
    async def call_tool(self, server, tool, arguments):
        return {"mock": True}


@pytest.mark.asyncio
async def test_planner_decomposes() -> None:
    agent = PlannerAgent(name="planner")
    result = await agent.execute({"text": "build a web app"})
    assert "plan" in result
    assert "route" in result


@pytest.mark.asyncio
async def test_coding_agent_writes() -> None:
    agent = CodingAgent(name="coding")
    result = await agent.execute({"action": "write", "path": "/tmp/jarvis_test.py", "content": "print('hi')"})
    assert result["status"] == "written"


@pytest.mark.asyncio
async def test_research_agent_searches() -> None:
    agent = ResearchAgent(name="research", mcp_client=MockMCP())
    result = await agent.execute({"query": "python"})
    assert result["query"] == "python"


@pytest.mark.asyncio
async def test_analysis_agent() -> None:
    agent = AnalysisAgent(name="analysis")
    result = await agent.execute({"text": "analyze this"})
    assert result["status"] == "analyzed"
    assert "documents" in result


@pytest.mark.asyncio
async def test_communication_agent_drafts() -> None:
    agent = CommunicationAgent(name="communication")
    result = await agent.execute({"action": "draft", "channel": "email", "to": "user@example.com", "subject": "hi", "body": "hello"})
    assert result["status"] == "drafted"
    assert result.get("requires_confirmation") is True


@pytest.mark.asyncio
async def test_communication_agent_send_blocked() -> None:
    agent = CommunicationAgent(name="communication")
    result = await agent.execute({"action": "send", "channel": "email", "to": "user@example.com", "subject": "hi", "body": "hello"})
    assert result["status"] == "blocked"


@pytest.mark.asyncio
async def test_vision_agent_analyze() -> None:
    agent = VisionAutomationAgent(name="vision")
    result = await agent.execute({"action": "analyze", "image": "/tmp/nonexistent.png"})
    assert result["status"] == "analyzed"
    assert "screen_elements" in result


@pytest.mark.asyncio
async def test_fast_response_agent() -> None:
    agent = FastResponseAgent(name="fast")
    result = await agent.execute({"text": "ping"})
    assert "response" in result
    assert "latency_ms" in result
