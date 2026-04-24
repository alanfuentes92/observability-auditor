from src.renderer.html_renderer import HTMLRenderer
from src.models import AuditResult, Finding, CheckStatus, BlastRadius


def test_render_produces_html():
    results = [
        AuditResult("oneagent_activegate", "infrastructure",
            [Finding("H-1", "prod-web-01", "host_monitoring", CheckStatus.PASS, "FULL_STACK", "", BlastRadius.CRITICAL),
             Finding("H-2", "dev-db-01", "host_monitoring", CheckStatus.FAIL, "DISCOVERY", "Enable FULL_STACK", BlastRadius.CRITICAL)],
            50.0, {"total": 2, "passed": 1, "failed": 1, "warned": 0}, {}, 150),
    ]
    analyses = {"oneagent_activegate": "## Analysis\nSome analysis text"}
    executive = "## Executive Summary\nOverall assessment"
    renderer = HTMLRenderer()
    html = renderer.render(results=results, analyses=analyses, executive_summary=executive,
        tenant_url="https://test.apps.dynatrace.com", global_score=50.0, category_scores={"infrastructure": 50.0})
    assert "<!DOCTYPE html>" in html
    assert "prod-web-01" in html
    assert "Observability Auditor" in html


def test_render_empty_results():
    renderer = HTMLRenderer()
    html = renderer.render(results=[], analyses={}, executive_summary="No data",
        tenant_url="https://test.apps.dynatrace.com", global_score=0.0, category_scores={})
    assert "<!DOCTYPE html>" in html


def test_render_contains_interactivity():
    results = [AuditResult("test", "dem", [], 85.0, {"total": 0, "passed": 0, "failed": 0, "warned": 0}, {}, 50)]
    renderer = HTMLRenderer()
    html = renderer.render(results=results, analyses={}, executive_summary="",
        tenant_url="https://t.com", global_score=85.0, category_scores={"dem": 85.0})
    assert "addEventListener" in html  # JS interactivity
    assert "@media print" in html      # Print CSS
