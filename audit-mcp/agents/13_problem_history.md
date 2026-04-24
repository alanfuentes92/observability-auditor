# Agent 13: Problem History & Operational Health

**Category:** operations
**Blast Radius:** HIGH / MEDIUM

## Purpose

Analyze problem history patterns to assess operational maturity: problem diversity, resolution times, affected users, and availability trends.

## MCP Tools

### Tool 1: Full problem history (30d)

```tool
list_problems(timeframe="30d", maxProblemsToDisplay=100)
```

### Tool 2: Active problems

```tool
list_problems(timeframe="7d", status="ACTIVE", maxProblemsToDisplay=20)
```

## Checks

### Check: availability_problems
- **Per entity:** TENANT
- **PASS:** < 5 AVAILABILITY category problems in 30 days
- **WARN:** 5-15 AVAILABILITY problems
- **FAIL:** > 15 AVAILABILITY problems (frequent outages)
- **Blast Radius:** HIGH
- **Remediation:** "High availability problem count ({count}) — investigate infrastructure stability"

### Check: active_problems_exist
- **Per entity:** TENANT
- **PASS:** No ACTIVE (unresolved) problems right now
- **WARN:** 1-3 active problems
- **FAIL:** > 3 active problems (ongoing issues)
- **Blast Radius:** HIGH
- **Remediation:** "There are {count} active unresolved problems — investigate immediately"

### Check: user_impact
- **Per entity:** TENANT
- **PASS:** < 20% of problems affect users
- **WARN:** 20-50% of problems affect users
- **FAIL:** > 50% of problems affect users (poor protection of user experience)
- **Blast Radius:** HIGH
- **Remediation:** "{pct}% of problems affect users — improve early detection before user impact"

### Check: problem_category_diversity
- **Per entity:** TENANT
- **PASS:** Problems span >= 3 categories (AVAILABILITY, SLOWDOWN, ERROR, CUSTOM_ALERT, RESOURCE) — indicates broad monitoring
- **WARN:** Problems in only 1-2 categories — monitoring may have blind spots
- **Blast Radius:** MEDIUM
- **Remediation:** "Problems only detected in {categories} — review monitoring coverage for other problem types"

## Evaluation Notes

This agent focuses on operational outcomes rather than configuration. A well-configured tenant should have diverse problem categories (broad detection), low active problem count, quick resolution times, and minimal user impact.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- High availability problems: infrastructure instability — hosts going offline, network connectivity issues, or monitoring agents losing connection
- Active unresolved problems: either genuine ongoing issues nobody is addressing, or stale problems from decommissioned/offline entities that were never cleaned up
- Low problem category diversity: monitoring blind spots — e.g., only detecting availability but not slowdowns or errors means anomaly detection may be misconfigured

### Recommendations
1. **Investigate active problems immediately** — unresolved problems indicate either ongoing issues or stale state that needs cleanup
2. **Analyze availability problem patterns** — are they concentrated on specific hosts/times? May indicate scheduled maintenance windows not configured
3. **Review problem feed for stale entities** — decommissioned hosts still generating problems should be removed from monitoring
4. **Correlate problem spikes with change events** — deployments, config changes, or infrastructure changes often trigger problem clusters
5. **Set up a daily problem review** — 5-minute standup reviewing new problems prevents accumulation

### Next Steps
- Triage all active problems: resolve or close stale ones (effort: 30 min)
- Identify the top 3 entities generating availability problems (effort: 15 min via DQL)
- Configure maintenance windows for planned downtime (effort: 15 min)
- Set up a daily problem digest notification (effort: 15 min)
- Review and clean up monitoring for decommissioned entities (effort: 30 min)
