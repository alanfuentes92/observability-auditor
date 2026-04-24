from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class AnomalyDetectionAuditAgent(BaseAuditAgent):
    name = "anomaly_detection"
    category = "configuration"

    async def collect(self) -> dict:
        host_anomaly = await self.client.settings_v2("builtin:anomaly-detection.infrastructure-hosts")
        disk_anomaly = await self.client.settings_v2("builtin:anomaly-detection.infrastructure-disks")
        service_anomaly = await self.client.settings_v2("builtin:anomaly-detection.services")
        return {"host_anomaly": host_anomaly, "disk_anomaly": disk_anomaly, "service_anomaly": service_anomaly}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        for area, label in [("host_anomaly", "Host Anomaly Detection"), ("disk_anomaly", "Disk Anomaly Detection"), ("service_anomaly", "Service Anomaly Detection")]:
            settings = data[area]
            custom = [s for s in settings if s.get("scope") != "environment"]
            findings.append(Finding("TENANT", label, f"{area}_customized",
                CheckStatus.PASS if custom else CheckStatus.WARN,
                f"{len(custom)} custom rule(s), {len(settings)} total",
                f"Review and tune {label.lower()} thresholds for your environment", BlastRadius.HIGH))
        return findings
