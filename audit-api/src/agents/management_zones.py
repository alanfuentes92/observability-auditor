from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class ManagementZonesAuditAgent(BaseAuditAgent):
    name = "management_zones"
    category = "configuration"

    async def collect(self) -> dict:
        mzs = await self.client.settings_v2("builtin:management-zones")
        services = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("SERVICE")', "fields": "+managementZones", "from": "now-30d"})
        return {"managementZones": mzs, "services": services}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        mzs = data["managementZones"]
        services = data["services"]
        findings.append(Finding("TENANT", "Management Zone Configuration", "mz_exist",
            CheckStatus.PASS if mzs else CheckStatus.FAIL,
            f"{len(mzs)} management zone(s) defined",
            "Create management zones to segment visibility and permissions", BlastRadius.CRITICAL))
        for mz in mzs:
            val = mz.get("value", {})
            mz_name = val.get("name", "unnamed")
            rules = val.get("rules", [])
            findings.append(Finding(mz.get("objectId", ""), f"MZ: {mz_name}", "mz_has_rules",
                CheckStatus.PASS if rules else CheckStatus.FAIL,
                f"{len(rules)} rule(s)" if rules else "No rules defined",
                f"Add rules to management zone '{mz_name}'", BlastRadius.HIGH))
        in_mz = sum(1 for s in services if s.get("managementZones"))
        total = len(services)
        if total > 0:
            pct = (in_mz / total) * 100
            status = CheckStatus.PASS if pct >= 80 else (CheckStatus.WARN if pct >= 50 else CheckStatus.FAIL)
            findings.append(Finding("TENANT", "Service MZ Coverage", "service_mz_coverage", status,
                f"{in_mz}/{total} services ({pct:.0f}%) in a management zone",
                "Review MZ rules to cover all critical services", BlastRadius.HIGH))
        return findings
