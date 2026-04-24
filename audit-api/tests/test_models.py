from src.models import Finding, AuditResult, BlastRadius, CheckStatus


def test_finding_creation():
    f = Finding(
        entity_id="HOST-123", entity_name="prod-web-01",
        check="oneagent_installed", status=CheckStatus.PASS,
        detail="OneAgent installed and running", remediation="N/A",
        blast_radius=BlastRadius.CRITICAL,
    )
    assert f.entity_id == "HOST-123"
    assert f.status == CheckStatus.PASS
    assert f.blast_radius == BlastRadius.CRITICAL


def test_audit_result_pass_rate():
    findings = [
        Finding("HOST-1", "h1", "c1", CheckStatus.PASS, "ok", "", BlastRadius.HIGH),
        Finding("HOST-2", "h2", "c2", CheckStatus.FAIL, "bad", "fix it", BlastRadius.CRITICAL),
        Finding("HOST-3", "h3", "c3", CheckStatus.WARN, "meh", "consider", BlastRadius.MEDIUM),
    ]
    result = AuditResult(
        agent_name="test_agent", category="infrastructure",
        findings=findings, score=33.3,
        summary={"total": 3, "passed": 1, "failed": 1, "warned": 1},
        raw_data={}, duration_ms=150,
    )
    assert result.agent_name == "test_agent"
    assert len(result.findings) == 3


def test_finding_semaphore():
    f_pass = Finding("X", "x", "c", CheckStatus.PASS, "", "", BlastRadius.LOW)
    f_fail = Finding("X", "x", "c", CheckStatus.FAIL, "", "", BlastRadius.LOW)
    assert f_pass.status.emoji == "\U0001f7e2"
    assert f_fail.status.emoji == "\U0001f534"


def test_blast_radius_weight():
    assert BlastRadius.CRITICAL.weight == 4.0
    assert BlastRadius.HIGH.weight == 3.0
    assert BlastRadius.MEDIUM.weight == 2.0
    assert BlastRadius.LOW.weight == 1.0
