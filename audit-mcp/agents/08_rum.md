# Agent 08: Real User Monitoring (RUM)

**Category:** dem
**Blast Radius:** HIGH / MEDIUM

## Purpose

Verify that RUM applications are properly configured: enabled, full capture rate, tagged, with naming rules and conversion goals.

## DQL Queries

### Query 1: RUM applications

```dql
fetch dt.entity.application
| fields id, entity.name, applicationType, tags
| limit 100
```

### Query 2: RUM configuration (via settings)

```dql
fetch dt.setting
| filter schemaId == "builtin:rum.general"
| fields key, value, summary, scope
| limit 200
```

### Query 3: User action naming rules

```dql
fetch dt.setting
| filter schemaId == "builtin:rum.web.user-action-naming"
| fields key, value, summary, scope
| limit 200
```

## Checks

### Check: rum_apps_exist
- **Per entity:** TENANT
- **PASS:** At least one application entity exists
- **INFO:** No RUM applications found (no penalty — may be intentional)
- **Blast Radius:** HIGH
- **Remediation:** "No RUM applications detected — configure Real User Monitoring if web/mobile apps exist"

### Check: rum_enabled
- **Per entity:** Each application
- **PASS:** Application has RUM enabled (inferred from entity existence and settings)
- **FAIL:** RUM disabled for this application
- **Blast Radius:** HIGH
- **Remediation:** "Enable Real User Monitoring for '{entity.name}'"

### Check: rum_tags_applied
- **Per entity:** Each application
- **PASS:** Application has at least one tag
- **FAIL:** No tags on application
- **Blast Radius:** MEDIUM
- **Remediation:** "Apply at least one tag to RUM app '{entity.name}'"

### Check: rum_naming_rules
- **Per entity:** TENANT
- **PASS:** User action naming rules exist (settings found)
- **FAIL:** No naming rules configured
- **Blast Radius:** HIGH
- **Remediation:** "Configure user action naming rules for meaningful action names"

### Check: rum_conversion_goals
- **Per entity:** Each application
- **INFO:** Conversion goals are not directly queryable via DQL — register as INFO
- **Blast Radius:** MEDIUM
- **Remediation:** "Verify conversion goals are defined for '{entity.name}' in the Dynatrace UI"

### Check: rum_session_properties
- **Per entity:** Each application
- **INFO:** Session properties are not directly queryable via DQL — register as INFO
- **Blast Radius:** MEDIUM
- **Remediation:** "Verify session/user action properties exist for '{entity.name}' in the Dynatrace UI"

## DQL Fallback

Some RUM configuration (conversion goals, session properties, capture rate) may not be fully available via DQL `dt.setting`. For those, register as INFO findings with a note to verify manually in the UI.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- No RUM applications: either no web/mobile applications exist in the monitored environment, or RUM JavaScript injection hasn't been configured
- For backend-only or infrastructure-focused tenants, this is expected and not a gap
- If web applications exist (e.g., metabase, n8n dashboards), missing RUM means no visibility into end-user experience

### Recommendations
1. **Identify web applications** that should be monitored — check if any monitored services serve web UIs
2. **Enable RUM via auto-injection** if OneAgent is installed on web servers — it injects the RUM JavaScript automatically
3. **Configure user action naming rules** for meaningful action names instead of generic URLs
4. **Set up session properties** for business context (user role, plan tier, region)
5. **Define conversion goals** for key user journeys if applicable

### Next Steps
- Inventory web applications in the environment (effort: 15 min)
- Enable RUM auto-injection on web-facing hosts (effort: 10 min, may require app restart)
- Configure naming rules after initial data collection (~24h of data) (effort: 30 min)
- Set up 2-3 session properties for business context (effort: 20 min)
