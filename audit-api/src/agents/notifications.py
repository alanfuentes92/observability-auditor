from src.agents.base import BaseAuditAgent
from src.models import BlastRadius, CheckStatus, Finding


class NotificationsAuditAgent(BaseAuditAgent):
    name = "problem_notifications"
    category = "configuration"

    async def collect(self) -> dict:
        notifications = await self.client.settings_v2("builtin:problem.notifications")
        alerting_profiles = await self.client.settings_v2("builtin:alerting.profile")
        return {"notifications": notifications, "alertingProfiles": alerting_profiles}

    def analyze(self, data: dict) -> list[Finding]:
        findings: list[Finding] = []
        notifs = data["notifications"]
        profiles = data["alertingProfiles"]
        findings.append(Finding("TENANT", "Problem Notification Config", "notifications_exist",
            CheckStatus.PASS if notifs else CheckStatus.FAIL,
            f"{len(notifs)} notification integration(s)",
            "Configure at least one problem notification channel", BlastRadius.CRITICAL))
        types_seen = set()
        for n in notifs:
            val = n.get("value", {})
            ntype = val.get("type", val.get("notificationType", "unknown"))
            types_seen.add(ntype)
        findings.append(Finding("TENANT", "Notification Diversity", "notification_diversity",
            CheckStatus.PASS if len(types_seen) >= 2 else CheckStatus.WARN,
            f"{len(types_seen)} notification type(s): {', '.join(types_seen) or 'none'}",
            "Use at least 2 different notification channels for redundancy", BlastRadius.HIGH))
        findings.append(Finding("TENANT", "Alerting Profiles", "alerting_profiles_exist",
            CheckStatus.PASS if profiles else CheckStatus.FAIL,
            f"{len(profiles)} alerting profile(s)",
            "Create custom alerting profiles to filter noise and route alerts", BlastRadius.HIGH))
        for p in profiles:
            val = p.get("value", {})
            p_name = val.get("name", "unnamed")
            rules = val.get("severityRules", val.get("rules", []))
            findings.append(Finding(p.get("objectId", ""), f"Profile: {p_name}", "profile_has_filters",
                CheckStatus.PASS if rules else CheckStatus.WARN,
                f"{len(rules)} filter rule(s)",
                f"Add severity or tag filters to alerting profile '{p_name}'", BlastRadius.MEDIUM))
        return findings
