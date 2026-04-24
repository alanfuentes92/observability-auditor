import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.orchestrator import Orchestrator
from src.client.dynatrace import DynatraceClient
from src.models import AuditResult


@pytest.fixture
def client():
    return DynatraceClient(tenant_url="https://test.live.dynatrace.com", api_token="test")


async def test_orchestrator_runs_all_agents(client):
    mock_result = AuditResult("mock", "test", [], 80.0, {"total": 0}, {}, 10)
    with patch("src.orchestrator.ALL_AGENTS") as mock_agents:
        mock_agent_cls = MagicMock()
        mock_agent_cls.return_value.run = AsyncMock(return_value=mock_result)
        mock_agents.__iter__ = lambda self: iter([mock_agent_cls, mock_agent_cls])
        orch = Orchestrator(client)
        results = await orch.run_all()
        assert len(results) == 2
        assert all(r.score == 80.0 for r in results)


async def test_orchestrator_handles_agent_failure(client):
    mock_ok = AuditResult("ok", "test", [], 90.0, {}, {}, 10)
    with patch("src.orchestrator.ALL_AGENTS") as mock_agents:
        ok_cls = MagicMock()
        ok_cls.return_value.run = AsyncMock(return_value=mock_ok)
        fail_cls = MagicMock(__name__="FailingAgent")
        fail_cls.return_value.run = AsyncMock(side_effect=Exception("API down"))
        fail_cls.return_value.name = "failing_agent"
        fail_cls.return_value.category = "test"
        mock_agents.__iter__ = lambda self: iter([ok_cls, fail_cls])
        orch = Orchestrator(client)
        results = await orch.run_all()
        assert len(results) == 2
