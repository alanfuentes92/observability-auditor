from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class SyntheticAuditAgent(BaseAuditAgent):
    name = "synthetic_monitors"
    category = "dem"

    async def collect(self) -> dict:
        monitors_resp = await self.client.api_v1("/api/v1/synthetic/monitors")
        monitors = monitors_resp.get("monitors", [])
        detailed = []
        for m in monitors:
            mid = m.get("entityId", "")
            try:
                detail = await self.client.api_v1(f"/api/v1/synthetic/monitors/{mid}")
                detailed.append(detail)
            except Exception:
                detailed.append(m)
        locations_resp = await self.client.api_v2("/api/v2/synthetic/locations")
        return {"monitors": detailed, "locations": {loc["entityId"]: loc for loc in locations_resp.get("locations", [])}}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        for monitor in data["monitors"]:
            eid = monitor.get("entityId", "")
            name = monitor.get("name", eid)
            mtype = monitor.get("type", "UNKNOWN")
            is_browser = mtype == "BROWSER"
            type_label = "Browser" if is_browser else "HTTP"
            enabled = monitor.get("enabled", False)
            findings.append(Finding(eid, name, "synthetic_enabled",
                CheckStatus.PASS if enabled else CheckStatus.FAIL,
                f"{type_label} monitor enabled: {enabled}", f"Enable {type_label} monitor '{name}'", BlastRadius.HIGH))
            assigned_locs = monitor.get("locations", [])
            findings.append(Finding(eid, name, "synthetic_multi_location",
                CheckStatus.PASS if len(assigned_locs) >= 2 else CheckStatus.FAIL,
                f"{len(assigned_locs)} location(s) assigned", f"Add at least 2 locations to '{name}'", BlastRadius.HIGH))
            tags = monitor.get("tags", [])
            findings.append(Finding(eid, name, "synthetic_tags",
                CheckStatus.PASS if tags else CheckStatus.FAIL,
                f"{len(tags)} tag(s)", f"Apply tags to synthetic monitor '{name}'", BlastRadius.MEDIUM))
            outage = monitor.get("anomalyDetection", {})
            outage_handling = outage.get("outageHandling", {})
            outage_enabled = outage_handling.get("globalOutage", False) or outage_handling.get("localOutage", False)
            findings.append(Finding(eid, name, "synthetic_outage_detection",
                CheckStatus.PASS if outage_enabled else CheckStatus.FAIL,
                f"Outage detection: {'enabled' if outage_enabled else 'disabled'}",
                f"Enable outage detection for '{name}'", BlastRadius.HIGH))
            if is_browser:
                script = monitor.get("script", {})
                events = script.get("events", [])
                if events:
                    first_has_val = bool(events[0].get("validate", []))
                    last_has_val = bool(events[-1].get("validate", [])) if len(events) > 1 else first_has_val
                    findings.append(Finding(eid, name, "synthetic_step_validation",
                        CheckStatus.PASS if (first_has_val and last_has_val) else CheckStatus.WARN,
                        f"First step validation: {first_has_val}, Last step validation: {last_has_val}",
                        f"Add validation rules to first and last steps of '{name}'", BlastRadius.HIGH))
        return findings
