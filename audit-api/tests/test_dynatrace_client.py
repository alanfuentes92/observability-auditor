import pytest
from src.client.dynatrace import DynatraceClient


@pytest.fixture
def client():
    return DynatraceClient(tenant_url="https://test123.live.dynatrace.com", api_token="dt0c01.TEST")


async def test_api_v2_get(client, httpx_mock):
    httpx_mock.add_response(
        url="https://test123.live.dynatrace.com/api/v2/entities?entitySelector=type%28%22HOST%22%29",
        json={"entities": [{"entityId": "HOST-1"}], "totalCount": 1},
    )
    result = await client.api_v2("/api/v2/entities", params={"entitySelector": 'type("HOST")'})
    assert result["totalCount"] == 1


async def test_api_v2_pagination(client, httpx_mock):
    httpx_mock.add_response(
        url="https://test123.live.dynatrace.com/api/v2/entities?entitySelector=type%28%22HOST%22%29",
        json={"entities": [{"entityId": "HOST-1"}], "nextPageKey": "page2", "totalCount": 2},
    )
    httpx_mock.add_response(
        url="https://test123.live.dynatrace.com/api/v2/entities?nextPageKey=page2",
        json={"entities": [{"entityId": "HOST-2"}], "totalCount": 2},
    )
    result = await client.api_v2_paginated("/api/v2/entities", params={"entitySelector": 'type("HOST")'})
    assert len(result) == 2


async def test_api_v1_get(client, httpx_mock):
    httpx_mock.add_response(
        url="https://test123.live.dynatrace.com/api/config/v1/managementZones",
        json={"values": [{"id": "mz-1", "name": "Prod"}]},
    )
    result = await client.api_v1("/api/config/v1/managementZones")
    assert result["values"][0]["name"] == "Prod"


async def test_auth_header(client, httpx_mock):
    httpx_mock.add_response(url="https://test123.live.dynatrace.com/api/v2/test", json={})
    await client.api_v2("/api/v2/test")
    request = httpx_mock.get_request()
    assert request.headers["Authorization"] == "Api-Token dt0c01.TEST"


async def test_retry_on_429(client, httpx_mock):
    httpx_mock.add_response(url="https://test123.live.dynatrace.com/api/v2/test", status_code=429)
    httpx_mock.add_response(url="https://test123.live.dynatrace.com/api/v2/test", json={"ok": True})
    result = await client.api_v2("/api/v2/test")
    assert result["ok"] is True
