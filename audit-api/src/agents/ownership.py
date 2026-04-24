from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class OwnershipAuditAgent(BaseAuditAgent):
    name = "ownership"
    category = "configuration"

    async def collect(self) -> dict:
        teams = await self.client.settings_v2("builtin:ownership.teams")
        services = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("SERVICE")', "fields": "+properties,+tags", "from": "now-30d"})
        return {"teams": teams, "services": services}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        teams = data["teams"]
        services = data["services"]
        findings.append(Finding("TENANT", "Ownership Teams", "teams_defined",
            CheckStatus.PASS if teams else CheckStatus.FAIL,
            f"{len(teams)} team(s) defined",
            "Define ownership teams in Dynatrace for accountability", BlastRadius.HIGH))
        owned = 0
        for svc in services:
            tags = svc.get("tags", [])
            has_owner = any(t.get("key", "").lower() in ("owner", "team", "squad") for t in tags)
            if has_owner:
                owned += 1
            else:
                findings.append(Finding(svc.get("entityId", ""), svc.get("displayName", "Unknown"),
                    "service_has_owner", CheckStatus.FAIL, "No owner/team tag assigned",
                    f"Assign an owner tag to service '{svc.get('displayName', '')}'", BlastRadius.HIGH))
        total = len(services)
        if total > 0:
            pct = (owned / total) * 100
            status = CheckStatus.PASS if pct >= 50 else (CheckStatus.WARN if pct >= 20 else CheckStatus.FAIL)
            findings.append(Finding("TENANT", "Service Ownership Coverage", "service_ownership_coverage", status,
                f"{owned}/{total} services ({pct:.0f}%) have an owner tag",
                "Apply owner/team tags to all critical services", BlastRadius.HIGH))
        return findings
