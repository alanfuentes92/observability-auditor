# Agent 04: Auto Tags

**Category:** configuration
**Blast Radius:** HIGH / MEDIUM

## Purpose

Verify that auto-tagging rules exist, have conditions, and provide adequate host coverage.

## DQL Queries

### Query 1: Auto-tag rules

```dql
fetch dt.setting
| filter schemaId == "builtin:tags.auto-tagging"
| fields key, value, summary, scope
| limit 200
```

### Query 2: Host tag coverage

```dql
fetch dt.entity.host
| fields id, entity.name, tags
| limit 500
```

## Checks

### Check: auto_tag_rules_exist
- **Per entity:** TENANT
- **PASS:** At least one auto-tag rule exists
- **FAIL:** No auto-tag rules configured
- **Blast Radius:** HIGH
- **Remediation:** "Create auto-tag rules to classify entities automatically"

### Check: host_tag_coverage
- **Per entity:** TENANT
- **PASS:** >= 80% of hosts have at least one tag
- **WARN:** 50-79% coverage
- **FAIL:** < 50% coverage
- **Blast Radius:** HIGH
- **Remediation:** "Only {pct}% of hosts have tags — review auto-tag rules to ensure all hosts are classified"

### Check: auto_tag_has_conditions
- **Per entity:** Each auto-tag rule
- **PASS:** Rule value contains conditions (non-empty conditions array)
- **FAIL:** Rule has no conditions
- **Blast Radius:** MEDIUM
- **Remediation:** "Add conditions to auto-tag rule '{rule_name}'"

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- Low tag coverage: no auto-tagging rules configured, so entities only get tags from manual application or cloud integrations (e.g., k8s labels)
- Without auto-tags, entity classification is inconsistent and scales poorly as the environment grows

### Recommendations
1. **Create auto-tag rules for common dimensions**: environment (prod/dev/lab), team/owner, application-tier (frontend/backend/database)
2. **Use hostname patterns** for host tagging (e.g., `*-lab-*` → environment:lab)
3. **Leverage Kubernetes labels** as auto-tag sources for k8s workloads
4. **Tag by technology** — auto-tag based on detected technologies (Java, .NET, Node.js)

### Next Steps
- Define tagging taxonomy: which tag keys and values to standardize (effort: 30 min)
- Create 3-5 auto-tag rules in Settings → Tags → Auto-tagging (effort: 15 min per rule)
- Verify tag propagation after 10-15 min (effort: 5 min)
- Review and clean up any manual tags that conflict with auto-tags (effort: 15 min)
