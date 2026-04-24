from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class AutoTagsAuditAgent(BaseAuditAgent):
    name = "auto_tags"
    category = "configuration"

    async def collect(self) -> dict:
        rules = await self.client.settings_v2("builtin:tags.auto-tagging")
        hosts = await self.client.api_v2_paginated(
            "/api/v2/entities", params={"entitySelector": 'type("HOST")', "fields": "+tags", "from": "now-30d"})
        return {"rules": rules, "hosts": hosts}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        rules = data["rules"]
        hosts = data["hosts"]
        findings.append(Finding("TENANT", "Auto Tag Configuration", "auto_tag_rules_exist",
            CheckStatus.PASS if rules else CheckStatus.FAIL,
            f"{len(rules)} auto-tag rules defined",
            "Create auto-tag rules to classify entities automatically", BlastRadius.HIGH))
        tagged = sum(1 for h in hosts if h.get("tags"))
        total = len(hosts)
        if total > 0:
            pct = (tagged / total) * 100
            status = CheckStatus.PASS if pct >= 80 else (CheckStatus.WARN if pct >= 50 else CheckStatus.FAIL)
            findings.append(Finding("TENANT", "Host Tag Coverage", "host_tag_coverage", status,
                f"{tagged}/{total} hosts ({pct:.0f}%) have at least one tag",
                "Review auto-tag rules to ensure all hosts are classified", BlastRadius.HIGH))
        for rule in rules:
            val = rule.get("value", {})
            rule_name = val.get("name", "unnamed")
            conditions = val.get("rules", [])
            findings.append(Finding(rule.get("objectId", ""), f"Rule: {rule_name}",
                "auto_tag_has_conditions",
                CheckStatus.PASS if conditions else CheckStatus.WARN,
                f"{len(conditions)} condition(s)" if conditions else "No conditions defined",
                f"Add conditions to auto-tag rule '{rule_name}'", BlastRadius.MEDIUM))
        return findings
