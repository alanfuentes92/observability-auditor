from src.models import Finding, AuditResult, CheckStatus, BlastRadius
from src.scoring.engine import ScoringEngine


def _make_finding(status: CheckStatus, blast: BlastRadius) -> Finding:
    return Finding("X", "x", "c", status, "", "", blast)


def test_agent_score_all_pass():
    findings = [_make_finding(CheckStatus.PASS, BlastRadius.CRITICAL), _make_finding(CheckStatus.PASS, BlastRadius.HIGH)]
    assert ScoringEngine.calculate_agent_score(findings) == 100.0


def test_agent_score_all_fail():
    findings = [_make_finding(CheckStatus.FAIL, BlastRadius.CRITICAL), _make_finding(CheckStatus.FAIL, BlastRadius.HIGH)]
    assert ScoringEngine.calculate_agent_score(findings) == 0.0


def test_agent_score_mixed():
    findings = [_make_finding(CheckStatus.PASS, BlastRadius.CRITICAL), _make_finding(CheckStatus.FAIL, BlastRadius.LOW)]
    assert ScoringEngine.calculate_agent_score(findings) == 80.0


def test_agent_score_warn_counts_half():
    findings = [_make_finding(CheckStatus.WARN, BlastRadius.CRITICAL), _make_finding(CheckStatus.PASS, BlastRadius.CRITICAL)]
    assert ScoringEngine.calculate_agent_score(findings) == 75.0


def test_global_score():
    results = [
        AuditResult("a", "infrastructure", [], 100.0, {}, {}, 0),
        AuditResult("b", "infrastructure", [], 50.0, {}, {}, 0),
    ]
    assert ScoringEngine.calculate_global_score(results) == 75.0


def test_category_scores():
    results = [
        AuditResult("a", "infrastructure", [], 90.0, {}, {}, 0),
        AuditResult("b", "dem", [], 60.0, {}, {}, 0),
        AuditResult("c", "configuration", [], 40.0, {}, {}, 0),
    ]
    cats = ScoringEngine.category_scores(results)
    assert cats["infrastructure"] == 90.0
    assert cats["dem"] == 60.0
    assert cats["configuration"] == 40.0


def test_semaphore():
    assert ScoringEngine.semaphore(85) == "green"
    assert ScoringEngine.semaphore(55) == "yellow"
    assert ScoringEngine.semaphore(30) == "red"
