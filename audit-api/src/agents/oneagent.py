from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class OneAgentAuditAgent(BaseAuditAgent):
    name = "oneagent_activegate"
    category = "infrastructure"

    async def collect(self) -> dict:
        hosts = await self.client.api_v2_paginated(
            "/api/v2/entities",
            params={"entitySelector": 'type("HOST")', "fields": "+properties", "from": "now-30d"},
        )
        ag_resp = await self.client.api_v2("/api/v2/activeGates")
        return {"hosts": hosts, "activeGates": ag_resp.get("activeGates", [])}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        for host in data["hosts"]:
            eid = host.get("entityId", "")
            name = host.get("displayName", eid)
            props = host.get("properties", {})
            mode = props.get("monitoringMode", "DISCOVERY")
            findings.append(Finding(eid, name, "host_monitoring_enabled",
                CheckStatus.PASS if mode == "FULL_STACK" else CheckStatus.FAIL,
                f"Monitoring mode: {mode}", "Set monitoring mode to FULL_STACK", BlastRadius.CRITICAL))
            versions = props.get("agentVersions", [])
            findings.append(Finding(eid, name, "oneagent_installed",
                CheckStatus.PASS if versions else CheckStatus.FAIL,
                f"Agent versions: {versions}" if versions else "No agent detected",
                "Install OneAgent on this host", BlastRadius.CRITICAL))
            state = props.get("state", "UNKNOWN")
            findings.append(Finding(eid, name, "host_state_running",
                CheckStatus.PASS if state == "RUNNING" else CheckStatus.WARN,
                f"Host state: {state}", "Investigate host state", BlastRadius.HIGH))
        for ag in data["activeGates"]:
            ag_id = ag.get("id", "")
            ag_name = ag.get("hostname", ag_id)
            connected = ag.get("connected", False)
            findings.append(Finding(ag_id, ag_name, "activegate_connected",
                CheckStatus.PASS if connected else CheckStatus.FAIL,
                f"Connected: {connected}", "Check ActiveGate process and network", BlastRadius.CRITICAL))
        if not data["activeGates"]:
            findings.append(Finding("NONE", "No ActiveGates", "activegate_exists",
                CheckStatus.WARN, "No ActiveGates found", "Consider deploying an ActiveGate", BlastRadius.HIGH))
        return findings
