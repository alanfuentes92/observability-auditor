# Agent 12: SLOs

**Category:** configuration
**Blast Radius:** HIGH / MEDIUM

## Purpose

Verify that SLOs are defined, have targets, burn rate alerts, and are in healthy status.

## DQL Queries

### Query 1: SLO entities

```dql
fetch dt.entity.slo
| fields id, entity.name, status, target, relatedEntity
| limit 200
```

### Query 2: SLO burn rate settings

```dql
fetch dt.setting
| filter schemaId == "builtin:monitoring.slo"
| fields key, value, summary, scope
| limit 200
```

## Checks

### Check: slos_exist
- **Per entity:** TENANT
- **PASS:** At least one SLO is defined
- **FAIL:** No SLOs configured
- **Blast Radius:** HIGH
- **Remediation:** "Define SLOs for critical services to set measurable reliability targets"

### Check: slo_has_target
- **Per entity:** Each SLO
- **PASS:** SLO has a target value set
- **FAIL:** No target defined
- **Blast Radius:** HIGH
- **Remediation:** "Set an SLO target for '{entity.name}'"

### Check: slo_burn_rate_alert
- **Per entity:** Each SLO
- **PASS:** Burn rate alert or related alerting config exists
- **WARN:** No burn rate alert configured
- **Blast Radius:** HIGH
- **Remediation:** "Configure a burn rate alert for SLO '{entity.name}'"

### Check: slo_status_healthy
- **Per entity:** Each SLO
- **PASS:** status == "SUCCESS"
- **WARN:** status != "SUCCESS"
- **Blast Radius:** MEDIUM
- **Remediation:** "Investigate SLO '{entity.name}' — status is '{status}'"

## DQL Fallback

If `dt.entity.slo` is not available, try:

```dql
fetch dt.setting
| filter schemaId == "builtin:monitoring.slo"
| fields key, value, summary, scope
| limit 200
```

Parse SLO definitions from the settings values.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- No SLOs: the organization hasn't adopted SLO-based reliability management — monitoring is reactive (respond to problems) rather than proactive (measure against targets)
- Without SLOs, there's no objective answer to "is this service reliable enough?" — decisions are based on gut feeling rather than data
- SLO adoption requires cultural shift: teams must agree on reliability targets and accept error budgets

### Recommendations
1. **Start with 2-3 SLOs for the most critical services** — availability and latency are the easiest to define
2. **Set realistic targets** — 99.5% availability for internal tools, 99.9% for customer-facing
3. **Configure burn rate alerts** — alert when error budget is being consumed too fast, not when SLO is breached
4. **Use SLOs to drive prioritization** — when error budget is healthy, ship features; when it's low, focus on reliability
5. **Review SLOs quarterly** — adjust targets based on actual performance and business needs

### Next Steps
- Identify top 3 services for initial SLO creation (effort: 15 min with team)
- Define availability SLOs using service request success rate metric (effort: 15 min per SLO)
- Configure burn rate alerts with 1h/6h/24h windows (effort: 10 min per SLO)
- Create an SLO dashboard for visibility (effort: 20 min)
- Schedule quarterly SLO review (effort: 5 min to set up recurring meeting)
