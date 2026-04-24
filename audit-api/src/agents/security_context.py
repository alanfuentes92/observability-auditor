from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class SecurityContextAuditAgent(BaseAuditAgent):
    name = "security_context"
    category = "configuration"

    async def collect(self) -> dict:
        contexts = await self.client.settings_v2("builtin:dt.security.context")
        return {"contexts": contexts}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        contexts = data["contexts"]
        findings.append(Finding("TENANT", "Security Context Configuration", "security_context_configured",
            CheckStatus.PASS if contexts else CheckStatus.FAIL,
            f"{len(contexts)} security context rule(s)" if contexts else "No security context configured",
            "Configure dt.security_context for data segmentation and compliance", BlastRadius.HIGH))
        context_names = [c.get("value", {}).get("name", "") for c in contexts]
        env_keywords = {"prod", "production", "dev", "development", "staging", "test", "qa"}
        has_env_separation = any(any(kw in name.lower() for kw in env_keywords) for name in context_names)
        if contexts:
            findings.append(Finding("TENANT", "Environment Separation", "env_separation",
                CheckStatus.PASS if has_env_separation else CheckStatus.WARN,
                "Environment-based security contexts detected" if has_env_separation else "No environment-based naming detected",
                "Use security contexts to separate prod/dev/staging data access", BlastRadius.CRITICAL))
        return findings
