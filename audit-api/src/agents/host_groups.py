from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class HostGroupsAuditAgent(BaseAuditAgent):
    name = "host_groups"
    category = "infrastructure"

    async def collect(self) -> dict:
        hosts = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("HOST")', "fields": "+properties.hostGroupName", "from": "now-30d"})
        host_groups = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("HOST_GROUP")', "from": "now-30d"})
        return {"hosts": hosts, "hostGroups": host_groups}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        hosts = data["hosts"]
        groups = data["hostGroups"]
        findings.append(Finding("TENANT", "Host Group Configuration", "host_groups_exist",
            CheckStatus.PASS if groups else CheckStatus.FAIL,
            f"{len(groups)} host group(s) defined",
            "Create host groups to organize infrastructure logically", BlastRadius.HIGH))
        assigned = sum(1 for h in hosts if h.get("properties", {}).get("hostGroupName"))
        total = len(hosts)
        if total > 0:
            pct = (assigned / total) * 100
            status = CheckStatus.PASS if pct >= 90 else (CheckStatus.WARN if pct >= 50 else CheckStatus.FAIL)
            findings.append(Finding("TENANT", "Host Group Assignment", "hosts_in_groups", status,
                f"{assigned}/{total} hosts ({pct:.0f}%) assigned to a host group",
                "Assign orphan hosts to appropriate host groups", BlastRadius.HIGH))
        for h in hosts:
            if not h.get("properties", {}).get("hostGroupName"):
                findings.append(Finding(h.get("entityId", ""), h.get("displayName", "Unknown"),
                    "host_in_group", CheckStatus.FAIL, "Host not assigned to any host group",
                    f"Assign {h.get('displayName', 'this host')} to a host group", BlastRadius.HIGH))
        return findings
