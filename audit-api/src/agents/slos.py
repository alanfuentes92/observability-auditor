from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class SlosAuditAgent(BaseAuditAgent):
    name = "slos"
    category = "configuration"

    async def collect(self) -> dict:
        slo_resp = await self.client.api_v2("/api/v2/slo", params={"pageSize": "500"})
        return {"slos": slo_resp.get("slo", [])}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        slos = data["slos"]
        findings.append(Finding("TENANT", "SLO Configuration", "slos_exist",
            CheckStatus.PASS if slos else CheckStatus.FAIL,
            f"{len(slos)} SLO(s) defined",
            "Define SLOs for critical services to set measurable reliability targets", BlastRadius.HIGH))
        for slo in slos:
            slo_id = slo.get("id", "")
            slo_name = slo.get("name", slo_id)
            target = slo.get("target")
            findings.append(Finding(slo_id, slo_name, "slo_has_target",
                CheckStatus.PASS if target else CheckStatus.FAIL,
                f"Target: {target}%" if target else "No target defined",
                f"Set an SLO target for '{slo_name}'", BlastRadius.HIGH))
            burn_rate = slo.get("burnRateConfig") or slo.get("metricExpression")
            has_alert = slo.get("hasAlert", False) or burn_rate is not None
            findings.append(Finding(slo_id, slo_name, "slo_burn_rate_alert",
                CheckStatus.PASS if has_alert else CheckStatus.WARN,
                f"Burn rate alert: {'configured' if has_alert else 'not configured'}",
                f"Configure a burn rate alert for SLO '{slo_name}'", BlastRadius.HIGH))
            status_val = slo.get("status", "UNKNOWN")
            findings.append(Finding(slo_id, slo_name, "slo_status_healthy",
                CheckStatus.PASS if status_val == "SUCCESS" else CheckStatus.WARN,
                f"Status: {status_val}",
                f"Investigate SLO '{slo_name}' — status is {status_val}", BlastRadius.MEDIUM))
        return findings
