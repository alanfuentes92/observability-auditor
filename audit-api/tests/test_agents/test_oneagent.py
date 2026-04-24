import pytest
from src.agents.oneagent import OneAgentAuditAgent
from src.client.dynatrace import DynatraceClient
from src.models import CheckStatus

BASE = "https://test.live.dynatrace.com"


@pytest.fixture
def client():
    return DynatraceClient(tenant_url=BASE, api_token="test")


async def test_oneagent_all_healthy(client, httpx_mock):
    httpx_mock.add_response(
        url=f'{BASE}/api/v2/entities?entitySelector=type%28%22HOST%22%29&fields=%2Bproperties&from=now-30d',
        json={"entities": [{"entityId": "HOST-1", "displayName": "prod-web-01",
            "properties": {"monitoringMode": "FULL_STACK", "agentVersions": [{"major": 1}], "state": "RUNNING"}}], "totalCount": 1})
    httpx_mock.add_response(
        url=f"{BASE}/api/v2/activeGates",
        json={"activeGates": [{"id": "AG-1", "hostname": "ag-01", "connected": True}]})
    agent = OneAgentAuditAgent(client)
    result = await agent.run()
    assert result.agent_name == "oneagent_activegate"
    assert result.category == "infrastructure"
    statuses = {f.check: f.status for f in result.findings}
    assert statuses["host_monitoring_enabled"] == CheckStatus.PASS
    assert statuses["activegate_connected"] == CheckStatus.PASS


async def test_oneagent_no_agent(client, httpx_mock):
    httpx_mock.add_response(
        url=f'{BASE}/api/v2/entities?entitySelector=type%28%22HOST%22%29&fields=%2Bproperties&from=now-30d',
        json={"entities": [{"entityId": "HOST-2", "displayName": "orphan",
            "properties": {"monitoringMode": "DISCOVERY", "state": "RUNNING"}}], "totalCount": 1})
    httpx_mock.add_response(
        url=f"{BASE}/api/v2/activeGates",
        json={"activeGates": []})
    agent = OneAgentAuditAgent(client)
    result = await agent.run()
    statuses = {f.check: f.status for f in result.findings}
    assert statuses["host_monitoring_enabled"] == CheckStatus.FAIL
