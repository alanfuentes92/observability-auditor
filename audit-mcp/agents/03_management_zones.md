# Agent 03: Management Zones

**Category:** configuration
**Blast Radius:** CRITICAL / HIGH

## Purpose

Verify that management zones are defined with rules, providing proper segmentation of visibility and permissions.

## DQL Queries

### Query 1: Management zone settings

```dql
fetch dt.setting
| filter schemaId == "builtin:management-zones"
| fields key, value, summary, scope
| limit 200
```

### Query 2: Service MZ coverage

```dql
fetch dt.entity.service
| fields id, entity.name, managementZones
| limit 500
```

## Checks

### Check: mz_exist
- **Per entity:** TENANT
- **PASS:** At least one management zone exists
- **FAIL:** No management zones defined
- **Blast Radius:** CRITICAL
- **Remediation:** "Create management zones to segment visibility and permissions"

### Check: mz_has_rules
- **Per entity:** Each MZ
- **PASS:** MZ value contains rules (rules array non-empty)
- **FAIL:** MZ has no rules defined
- **Blast Radius:** HIGH
- **Remediation:** "Add rules to management zone '{mz_name}'"

### Check: service_mz_coverage
- **Per entity:** TENANT
- **PASS:** >= 80% of services belong to at least one MZ
- **WARN:** 50-79% coverage
- **FAIL:** < 50% coverage
- **Blast Radius:** HIGH
- **Remediation:** "Only {pct}% of services are in management zones — target >= 80%"

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- No management zones: tenant was set up without RBAC or data segmentation planning — all users see everything, no permission boundaries
- 0% service coverage means no entity has been classified into any logical boundary
- dt.setting unavailability may mask existing MZ definitions — verify via UI

### Recommendations
1. **Create management zones by business function** — e.g., `Analytics` (metabase, bakedata), `Monitoring` (zabbix), `Automation` (n8n), `Platform` (k8s infra)
2. **Define MZ rules using tags or host groups** rather than individual entity selectors for maintainability
3. **Apply MZ-based permissions** to restrict visibility per team/role
4. **Use MZs in dashboards and alerting profiles** to reduce noise per team

### Next Steps
- Design MZ structure based on teams and services (effort: 30 min)
- Create MZs with rules in Settings → Management Zones (effort: 15 min per MZ)
- Validate service coverage after creation (effort: 10 min)
- Configure user permissions per MZ if multi-team access (effort: 30 min)
