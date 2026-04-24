from unittest.mock import AsyncMock
from src.analyzer.gemini_analyzer import GeminiAnalyzer
from src.models import AuditResult, Finding, CheckStatus, BlastRadius


async def test_analyze_section():
    mock_client = AsyncMock()
    mock_client.generate.return_value = "## Análisis\nTest analysis content"
    analyzer = GeminiAnalyzer(client=mock_client, tenant_url="https://test.apps.dynatrace.com")
    result = AuditResult("test", "infrastructure",
        [Finding("H-1", "host1", "check1", CheckStatus.PASS, "ok", "", BlastRadius.HIGH)],
        100.0, {"total": 1, "passed": 1, "failed": 0, "warned": 0}, {}, 100)
    text = await analyzer.analyze_section(result)
    assert "Análisis" in text
    mock_client.generate.assert_called_once()


async def test_analyze_executive():
    mock_client = AsyncMock()
    mock_client.generate.return_value = "## Resumen Ejecutivo\nAll good"
    analyzer = GeminiAnalyzer(client=mock_client, tenant_url="https://test.apps.dynatrace.com")
    results = [
        AuditResult("a1", "infrastructure", [], 90.0, {"passed": 5, "failed": 1}, {}, 100),
        AuditResult("a2", "dem", [], 60.0, {"passed": 3, "failed": 2}, {}, 200),
    ]
    text = await analyzer.analyze_executive(results)
    assert "Resumen" in text
