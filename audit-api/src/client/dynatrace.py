import asyncio
import httpx


class DynatraceClient:
    def __init__(
        self, tenant_url: str, api_token: str,
        oauth_client_id: str | None = None,
        oauth_client_secret: str | None = None,
        oauth_scope: str | None = None,
    ):
        self.tenant_url = tenant_url.rstrip("/")
        self.api_token = api_token
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.oauth_scope = oauth_scope
        self._oauth_token: str | None = None
        self._http = httpx.AsyncClient(timeout=30.0)

    async def _get_oauth_token(self) -> str:
        if self._oauth_token:
            return self._oauth_token
        resp = await self._http.post(
            "https://sso.dynatrace.com/sso/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.oauth_client_id,
                "client_secret": self.oauth_client_secret,
                "scope": self.oauth_scope or "",
            },
        )
        resp.raise_for_status()
        self._oauth_token = resp.json()["access_token"]
        return self._oauth_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Api-Token {self.api_token}", "Accept": "application/json"}

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        max_retries = 3
        for attempt in range(max_retries):
            resp = await self._http.request(method, url, **kwargs)
            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", 1))
                await asyncio.sleep(min(wait, 5))
                continue
            resp.raise_for_status()
            return resp
        resp.raise_for_status()
        return resp

    async def api_v2(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.tenant_url}{path}"
        resp = await self._request("GET", url, headers=self._headers(), params=params)
        return resp.json()

    async def api_v2_paginated(self, path: str, params: dict | None = None, key: str = "entities") -> list[dict]:
        all_items: list[dict] = []
        params = dict(params or {})
        while True:
            data = await self.api_v2(path, params=params)
            all_items.extend(data.get(key, []))
            next_page = data.get("nextPageKey")
            if not next_page:
                break
            params = {"nextPageKey": next_page}
        return all_items

    async def api_v1(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.tenant_url}{path}"
        resp = await self._request("GET", url, headers=self._headers(), params=params)
        return resp.json()

    async def settings_v2(self, schema_id: str) -> list[dict]:
        try:
            return await self.api_v2_paginated(
                "/api/v2/settings/objects",
                params={"schemaIds": schema_id, "pageSize": "500"},
                key="items",
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise

    async def close(self):
        await self._http.aclose()
