# Agent 06: Ownership

**Category:** configuration
**Blast Radius:** HIGH

## Purpose

Verify that ownership teams are defined and services have owner assignments for accountability.

## DQL Queries

### Query 1: Ownership teams

```dql
fetch dt.setting
| filter schemaId == "builtin:ownership.teams"
| fields key, value, summary, scope
| limit 200
```

### Query 2: Service ownership

```dql
fetch dt.entity.service
| fields id, entity.name, tags
| limit 500
```

## Checks

### Check: teams_defined
- **Per entity:** TENANT
- **PASS:** At least one ownership team exists
- **FAIL:** No teams defined
- **Blast Radius:** HIGH
- **Remediation:** "Define ownership teams in Dynatrace for accountability"

### Check: service_has_owner
- **Per entity:** Each service
- **PASS:** Service has a tag containing "owner", "team", or "squad" (case-insensitive)
- **FAIL:** No owner-related tag found
- **Blast Radius:** HIGH
- **Remediation:** "Assign an owner tag to service '{entity.name}'"

### Check: service_ownership_coverage
- **Per entity:** TENANT
- **PASS:** >= 50% of services have an owner tag
- **WARN:** 20-49%
- **FAIL:** < 20%
- **Blast Radius:** HIGH
- **Remediation:** "Only {pct}% of services have owners — apply owner/team tags to all critical services"

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- No ownership: Dynatrace Ownership feature not adopted — no teams defined, no owner tags on services
- Without ownership, there's no accountability during incidents — nobody knows who to page or escalate to
- This is a governance gap, not a technical limitation — Dynatrace supports ownership natively

### Recommendations
1. **Define ownership teams** in Settings → Ownership → Teams — map to your org structure
2. **Assign owner tags** to all services: use `owner:team-name` convention
3. **Start with critical services** — identify the top 5-10 services by traffic/revenue and assign owners first
4. **Integrate ownership with alerting profiles** — route problems to the owning team automatically
5. **Use Dynatrace Ownership dashboards** to track coverage and gaps

### Next Steps
- Map services to teams with service owners (effort: 1 hour with team leads)
- Create teams in Dynatrace Ownership (effort: 10 min per team)
- Apply owner tags via API for bulk assignment (effort: 30 min)
- Configure alerting profile routing based on ownership (effort: 30 min per profile)
