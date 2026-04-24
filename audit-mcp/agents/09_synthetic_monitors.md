# Agent 09: Synthetic Monitors

**Category:** dem
**Blast Radius:** HIGH / MEDIUM

## Purpose

Verify that synthetic monitors are configured, enabled, multi-location, tagged, and have outage detection.

## DQL Queries

### Query 1: Synthetic monitors

```dql
fetch dt.entity.synthetic_test
| fields id, entity.name, type, enabled, tags
| limit 200
```

### Query 2: Synthetic locations

```dql
fetch dt.entity.synthetic_location
| fields id, entity.name, type
| limit 100
```

### Query 3: Synthetic monitor settings

```dql
fetch dt.setting
| filter schemaId == "builtin:synthetic.browser" OR schemaId == "builtin:synthetic.http"
| fields key, value, summary, scope
| limit 200
```

## Checks

### Check: synthetic_monitors_exist
- **Per entity:** TENANT
- **PASS:** At least one synthetic monitor exists
- **INFO:** No synthetic monitors found (may be intentional)
- **Blast Radius:** HIGH
- **Remediation:** "No synthetic monitors detected — configure HTTP or browser monitors for critical endpoints"

### Check: synthetic_enabled
- **Per entity:** Each monitor
- **PASS:** enabled == true
- **FAIL:** enabled == false
- **Blast Radius:** HIGH
- **Remediation:** "Enable synthetic monitor '{entity.name}'"

### Check: synthetic_multi_location
- **Per entity:** Each monitor
- **PASS:** Monitor executes from >= 2 locations
- **FAIL:** Monitor uses only 1 location
- **Blast Radius:** HIGH
- **Remediation:** "Add at least 2 execution locations to '{entity.name}' for reliable outage detection"

### Check: synthetic_tags
- **Per entity:** Each monitor
- **PASS:** Monitor has at least one tag
- **FAIL:** No tags applied
- **Blast Radius:** MEDIUM
- **Remediation:** "Apply tags to synthetic monitor '{entity.name}'"

### Check: synthetic_outage_detection
- **Per entity:** Each monitor
- **PASS:** Outage detection config found in settings
- **FAIL:** No outage detection configuration
- **Blast Radius:** HIGH
- **Remediation:** "Enable outage detection for '{entity.name}'"

## DQL Fallback

Location count per monitor may not be directly available via entity fields. If not queryable, check the settings or register as INFO: "Location count not available via DQL — verify manually".

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- Monitors without tags: monitors were created ad-hoc without a tagging strategy — makes it hard to filter, group, and associate with teams/services
- Missing multi-location: monitors created with default single location — reduces reliability of outage detection (single point of failure in detection)
- No outage detection config: monitors may not trigger problems on failure — defeats the purpose of synthetic monitoring

### Recommendations
1. **Apply tags to all monitors** — at minimum: `client:name`, `environment:type`, `team:owner`
2. **Configure at least 2 execution locations** per monitor for reliable outage detection
3. **Enable outage detection** with appropriate consecutive-failure thresholds
4. **Add synthetic monitors for internal services** — not just external websites
5. **Review monitor frequency** — critical endpoints should run every 5-10 min

### Next Steps
- Tag all existing monitors via Dynatrace UI or API (effort: 5 min per monitor)
- Review and add execution locations to single-location monitors (effort: 5 min per monitor)
- Verify outage detection settings per monitor (effort: 10 min total)
- Identify internal endpoints that need synthetic monitors (effort: 30 min planning)
- Create monitors for critical internal services (effort: 15 min per monitor)
