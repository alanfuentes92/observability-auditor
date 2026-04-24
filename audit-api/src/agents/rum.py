from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class RumAuditAgent(BaseAuditAgent):
    name = "rum"
    category = "dem"

    async def collect(self) -> dict:
        apps = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("APPLICATION")', "fields": "+properties,+tags", "from": "now-365d"})
        app_configs = []
        for app in apps:
            app_id = app.get("entityId", "")
            try:
                config = await self.client.api_v1(f"/api/config/v1/applications/web/{app_id}")
                app_configs.append({"entity": app, "config": config})
            except Exception:
                app_configs.append({"entity": app, "config": None})
        return {"applications": app_configs}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        for app_data in data["applications"]:
            entity = app_data["entity"]
            config = app_data["config"]
            eid = entity.get("entityId", "")
            name = entity.get("displayName", eid)
            if config is None:
                findings.append(Finding(eid, name, "rum_config_accessible", CheckStatus.WARN,
                    "Could not retrieve RUM config", "Check API token scopes for ReadConfig", BlastRadius.HIGH))
                continue
            monitoring = config.get("realUserMonitoringEnabled", False)
            findings.append(Finding(eid, name, "rum_enabled",
                CheckStatus.PASS if monitoring else CheckStatus.FAIL,
                f"RUM enabled: {monitoring}", f"Enable Real User Monitoring for '{name}'", BlastRadius.HIGH))
            cost = config.get("costAndTrafficControl", {})
            pct = cost.get("trafficPercentage", 0)
            findings.append(Finding(eid, name, "rum_capture_rate",
                CheckStatus.PASS if pct == 100 else CheckStatus.WARN,
                f"Capture rate: {pct}%", f"Set capture rate to 100% for '{name}'", BlastRadius.HIGH))
            tags = entity.get("tags", [])
            findings.append(Finding(eid, name, "rum_tags_applied",
                CheckStatus.PASS if tags else CheckStatus.FAIL,
                f"{len(tags)} tag(s) applied", f"Apply at least one tag to RUM app '{name}'", BlastRadius.MEDIUM))
            naming = config.get("userActionNamingSettings", {})
            load_rules = naming.get("loadActionNamingRules", [])
            xhr_rules = naming.get("xhrActionNamingRules", [])
            total_rules = len(load_rules) + len(xhr_rules)
            findings.append(Finding(eid, name, "rum_naming_rules",
                CheckStatus.PASS if total_rules > 0 else CheckStatus.FAIL,
                f"{total_rules} naming rule(s)", f"Configure user action naming rules for '{name}'", BlastRadius.HIGH))
            goals = config.get("conversionGoals", [])
            findings.append(Finding(eid, name, "rum_conversion_goals",
                CheckStatus.PASS if goals else CheckStatus.FAIL,
                f"{len(goals)} conversion goal(s)", f"Define conversion goals for '{name}'", BlastRadius.MEDIUM))
            ua_props = config.get("userActionAndSessionProperties", [])
            findings.append(Finding(eid, name, "rum_session_properties",
                CheckStatus.PASS if ua_props else CheckStatus.FAIL,
                f"{len(ua_props)} session/action property(ies)", f"Add session or user action properties to '{name}'", BlastRadius.MEDIUM))
        return findings
