from src.storage.history import HistoryStore
from src.models import AuditResult


def test_save_and_list(tmp_path):
    store = HistoryStore(base_dir=str(tmp_path))
    results = [AuditResult("agent1", "infra", [], 85.0, {"total": 5}, {}, 100)]
    run_id = store.save("test123", results, {"agent1": "Some analysis"}, "Executive summary", "<html>report</html>")
    assert run_id is not None
    runs = store.list_runs("test123")
    assert len(runs) == 1
    assert runs[0]["run_id"] == run_id


def test_load_run(tmp_path):
    store = HistoryStore(base_dir=str(tmp_path))
    results = [AuditResult("agent1", "infra", [], 85.0, {"total": 5}, {"key": "val"}, 100)]
    run_id = store.save("t1", results, {"agent1": "analysis"}, "exec", "<html/>")
    loaded = store.load_run("t1", run_id)
    assert loaded["metadata"]["tenant_id"] == "t1"
    assert loaded["html"] == "<html/>"
    assert "agent1" in loaded["raw"]


def test_compare_runs(tmp_path):
    store = HistoryStore(base_dir=str(tmp_path))
    r1 = [AuditResult("a1", "infra", [], 60.0, {}, {}, 100)]
    r2 = [AuditResult("a1", "infra", [], 85.0, {}, {}, 100)]
    import time; id1 = store.save("t1", r1, {}, "", ""); time.sleep(1.1)
    id2 = store.save("t1", r2, {}, "", "")
    diff = store.compare("t1", id1, id2)
    assert diff["a1"]["before"] == 60.0
    assert diff["a1"]["after"] == 85.0
    assert diff["a1"]["delta"] == 25.0
