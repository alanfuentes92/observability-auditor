from urllib.parse import urlparse
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dt_tenant_url: str
    dt_api_token: str
    dt_oauth_client_id: str | None = None
    dt_oauth_client_secret: str | None = None
    dt_oauth_scope: str | None = None
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    history_dir: str = "~/.auditor/history"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def tenant_id(self) -> str:
        hostname = urlparse(self.dt_tenant_url).hostname or ""
        return hostname.split(".")[0]

    @property
    def config_api_url(self) -> str:
        return f"https://{self.tenant_id}.live.dynatrace.com"

    @property
    def env_api_url(self) -> str:
        return f"https://{self.tenant_id}.live.dynatrace.com"
