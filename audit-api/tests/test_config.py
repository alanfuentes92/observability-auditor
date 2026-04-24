from src.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DT_TENANT_URL", "https://test.apps.dynatrace.com")
    monkeypatch.setenv("DT_API_TOKEN", "dt0c01.TEST")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    s = Settings()
    assert s.dt_tenant_url == "https://test.apps.dynatrace.com"
    assert s.dt_api_token == "dt0c01.TEST"
    assert s.gemini_api_key == "test-key"
    assert s.gemini_model == "gemini-2.5-flash"


def test_settings_optional_oauth(monkeypatch):
    monkeypatch.setenv("DT_TENANT_URL", "https://test.apps.dynatrace.com")
    monkeypatch.setenv("DT_API_TOKEN", "dt0c01.TEST")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    s = Settings()
    assert s.dt_oauth_client_id is None
    assert s.dt_oauth_client_secret is None


def test_settings_tenant_id_derived(monkeypatch):
    monkeypatch.setenv("DT_TENANT_URL", "https://abc12345.apps.dynatrace.com")
    monkeypatch.setenv("DT_API_TOKEN", "dt0c01.TEST")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    s = Settings()
    assert s.tenant_id == "abc12345"
