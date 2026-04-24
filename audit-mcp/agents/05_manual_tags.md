# Agent 05: Manual Tags

**Category:** configuration
**Blast Radius:** MEDIUM

## Purpose

Evaluate the hygiene of manually applied tags across hosts and services — are they consistent, meaningful, and well-structured?

## DQL Queries

### Query 1: Host tags

```dql
fetch dt.entity.host
| fields id, entity.name, tags
| limit 500
```

### Query 2: Service tags

```dql
fetch dt.entity.service
| fields id, entity.name, tags
| limit 500
```

## Checks

### Check: entities_have_manual_tags
- **Per entity:** TENANT
- **PASS:** >= 70% of hosts+services have at least one manually applied tag
- **WARN:** 40-69%
- **FAIL:** < 40%
- **Blast Radius:** MEDIUM
- **Remediation:** "Only {pct}% of entities have manual tags — apply tags for environment, team, cost center"

### Check: tag_key_consistency
- **Per entity:** TENANT
- **PASS:** Tag keys follow a consistent naming pattern (e.g., no mixed case duplicates like "Environment" vs "environment")
- **WARN:** Inconsistent tag key casing or near-duplicates detected
- **Blast Radius:** MEDIUM
- **Remediation:** "Standardize tag keys — found inconsistent variants: {variants}"

## Evaluation Notes

To detect tag key inconsistency, group all tag keys, lowercase them, and check for duplicates. For example, if both "Environment" and "environment" exist, that's a WARN.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- Low manual tag coverage: teams haven't adopted a tagging discipline — tags are ad-hoc rather than systematic
- Some tags may come from integrations (k8s namespace labels) rather than intentional manual classification
- Tag inconsistency (mixed casing) indicates multiple people tagging without a shared standard

### Recommendations
1. **Establish a tagging standard document** — define allowed tag keys, casing convention (lowercase recommended), and required tags per entity type
2. **Prioritize manual tags for dimensions auto-tags can't cover**: cost-center, business-criticality, compliance-scope
3. **Audit and clean up existing tags** — remove duplicates, fix casing inconsistencies
4. **Prefer auto-tags over manual tags** where possible — manual tags should complement, not replace auto-tagging

### Next Steps
- Document tagging standard with 5-8 required tag keys (effort: 30 min)
- Apply missing tags to critical services via Dynatrace UI or API (effort: 5 min per entity)
- Set up a quarterly tag hygiene review process (effort: 15 min to document)
