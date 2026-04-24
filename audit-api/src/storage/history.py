import json
from datetime import datetime, timezone
from pathlib import Path
from src.models import AuditResult


class HistoryStore:
    def __init__(self, base_dir: str = "~/.auditor/history"):
        self.base = Path(base_dir).expanduser()

    def _run_dir(self, tenant_id: str, run_id: str) -> Path:
        return self.base / tenant_id / run_id

    def save(self, tenant_id: str, results: list[AuditResult],
             analyses: dict[str, str], executive_summary: str, html_report: str) -> str:
        run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        run_dir = self._run_dir(tenant_id, run_id)
        raw_dir = run_dir / "raw"
        analysis_dir = run_dir / "analysis"
        raw_dir.mkdir(parents=True, exist_ok=True)
        analysis_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "tenant_id": tenant_id, "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {r.agent_name: {"score": r.score, "category": r.category} for r in results},
        }
        (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        for r in results:
            (raw_dir / f"{r.agent_name}.json").write_text(json.dumps(r.raw_data, indent=2, default=str))
            # Persist findings for later re-rendering
            findings_data = [
                {"entity_id": f.entity_id, "entity_name": f.entity_name, "check": f.check,
                 "status": f.status.value, "detail": f.detail, "remediation": f.remediation,
                 "blast_radius": f.blast_radius.value}
                for f in r.findings
            ]
            agent_meta = {"score": r.score, "category": r.category, "summary": r.summary,
                          "duration_ms": r.duration_ms, "findings": findings_data}
            (raw_dir / f"{r.agent_name}_results.json").write_text(
                json.dumps(agent_meta, indent=2, ensure_ascii=False)
            )
        for agent_name, text in analyses.items():
            (analysis_dir / f"{agent_name}.md").write_text(text or "")
        if executive_summary:
            (analysis_dir / "executive_summary.md").write_text(executive_summary)
        (run_dir / "report.html").write_text(html_report)
        return run_id

    def list_runs(self, tenant_id: str) -> list[dict]:
        tenant_dir = self.base / tenant_id
        if not tenant_dir.exists():
            return []
        runs = []
        for d in sorted(tenant_dir.iterdir(), reverse=True):
            meta_file = d / "metadata.json"
            if meta_file.exists():
                runs.append(json.loads(meta_file.read_text()))
        return runs

    def load_run(self, tenant_id: str, run_id: str) -> dict:
        run_dir = self._run_dir(tenant_id, run_id)
        meta = json.loads((run_dir / "metadata.json").read_text())
        html = (run_dir / "report.html").read_text()
        raw = {}
        for f in (run_dir / "raw").glob("*.json"):
            raw[f.stem] = json.loads(f.read_text())
        return {"metadata": meta, "html": html, "raw": raw}

    def compare(self, tenant_id: str, run_id_before: str, run_id_after: str) -> dict:
        before = json.loads((self._run_dir(tenant_id, run_id_before) / "metadata.json").read_text())
        after = json.loads((self._run_dir(tenant_id, run_id_after) / "metadata.json").read_text())
        diff = {}
        all_agents = set(before.get("agents", {})) | set(after.get("agents", {}))
        for agent in all_agents:
            b_score = before.get("agents", {}).get(agent, {}).get("score", 0)
            a_score = after.get("agents", {}).get(agent, {}).get("score", 0)
            diff[agent] = {"before": b_score, "after": a_score, "delta": round(a_score - b_score, 1)}
        return diff
