from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class ManualTagsAuditAgent(BaseAuditAgent):
    name = "manual_tags"
    category = "configuration"

    async def collect(self) -> dict:
        services = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("SERVICE")', "fields": "+tags", "from": "now-30d"})
        apps = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("APPLICATION")', "fields": "+tags", "from": "now-30d"})
        return {"services": services, "applications": apps}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        for entity_type, entities in [("Service", data["services"]), ("Application", data["applications"])]:
            tagged = sum(1 for e in entities if e.get("tags"))
            total = len(entities)
            if total > 0:
                pct = (tagged / total) * 100
                status = CheckStatus.PASS if pct >= 70 else (CheckStatus.WARN if pct >= 30 else CheckStatus.FAIL)
                findings.append(Finding("TENANT", f"{entity_type} Tag Coverage",
                    f"{entity_type.lower()}_tag_coverage", status,
                    f"{tagged}/{total} {entity_type.lower()}s ({pct:.0f}%) have tags",
                    f"Apply tags to untagged {entity_type.lower()}s", BlastRadius.MEDIUM))
            for e in entities:
                if not e.get("tags"):
                    findings.append(Finding(e.get("entityId", ""), e.get("displayName", "Unknown"),
                        f"{entity_type.lower()}_has_tags", CheckStatus.FAIL,
                        f"No tags applied to this {entity_type.lower()}",
                        f"Apply at least one tag to {e.get('displayName', 'this entity')}", BlastRadius.MEDIUM))
        return findings
