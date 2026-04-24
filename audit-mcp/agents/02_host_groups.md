# Agent 02: Host Groups

**Category:** infrastructure
**Blast Radius:** HIGH

## Purpose

Verify that hosts are organized into host groups for structured management, monitoring, and update control.

## DQL Queries

### Query 1: Host group assignment

```dql
fetch dt.entity.host
| fields id, entity.name, hostGroupName = belongs_to[dt.entity.host_group]
| limit 500
```

### Query 2: Host group count

```dql
fetch dt.entity.host_group
| summarize count()
```

## Checks

### Check: host_groups_exist
- **Per entity:** TENANT
- **PASS:** At least one host group exists
- **FAIL:** No host groups defined
- **Blast Radius:** HIGH
- **Remediation:** "Create host groups to organize hosts by environment, team, or function"

### Check: host_assigned_to_group
- **Per entity:** Each host
- **PASS:** hostGroupName is non-null / non-empty
- **FAIL:** Host has no host group assignment
- **Blast Radius:** HIGH
- **Remediation:** "Assign host '{entity.name}' to a host group"

### Check: host_group_coverage
- **Per entity:** TENANT
- **PASS:** >= 80% of hosts assigned to a group
- **WARN:** 50-79% assigned
- **FAIL:** < 50% assigned
- **Blast Radius:** HIGH
- **Remediation:** "Only {pct}% of hosts are in host groups — target >= 80%"

## DQL Fallback

If `belongs_to[dt.entity.host_group]` is not available, try:

```dql
fetch dt.entity.host
| fields id, entity.name, tags
| filter contains(toString(tags), "HostGroup:")
```

If neither works, register INFO: "Host group assignment data not available via DQL".

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- No host groups: typically means Dynatrace was deployed without planning for segmentation — common in quick PoC or lab setups
- Without host groups, OneAgent update policies apply globally and there's no way to stage rollouts or differentiate monitoring settings by environment/role

### Recommendations
1. **Create host groups by function/environment** — e.g., `lab-servers`, `workstations`, `kubernetes-nodes`
2. **Assign all hosts** to their corresponding group during OneAgent config or via host group parameter
3. **Use host groups for staged OneAgent updates** — update lab first, then production

### Next Steps
- Define host group naming convention (effort: 10 min)
- Configure host group parameter in OneAgent config on each host (effort: 10 min per host, requires agent restart)
- Verify assignments in Dynatrace UI → Hosts → filter by host group (effort: 5 min)
