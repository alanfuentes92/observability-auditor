# Agent 07: Security Context

**Category:** configuration
**Blast Radius:** CRITICAL / HIGH

## Purpose

Verify that security contexts are configured for data segmentation and that environment separation (prod/dev/staging) is enforced.

## DQL Queries

### Query 1: Security context settings

```dql
fetch dt.setting
| filter schemaId == "builtin:dt.security.context"
| fields key, value, summary, scope
| limit 200
```

## Checks

### Check: security_context_configured
- **Per entity:** TENANT
- **PASS:** At least one security context rule exists
- **FAIL:** No security context rules configured
- **Blast Radius:** HIGH
- **Remediation:** "Configure dt.security_context for data segmentation and compliance"

### Check: env_separation
- **Per entity:** TENANT
- **PASS:** Context names/values contain environment keywords (prod, dev, staging, test, uat, pre-prod)
- **WARN:** No environment-based naming detected in contexts
- **Blast Radius:** CRITICAL
- **Remediation:** "Use security contexts to separate prod/dev/staging data access"

## Evaluation Notes

For env_separation, scan the value/summary fields of all security context settings for keywords: prod, production, dev, development, staging, test, uat, pre-prod, preprod. If any match, PASS. If contexts exist but none match environment keywords, WARN.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- dt.setting not available via DQL: likely the API token lacks `settings.read` scope, or the tenant version doesn't expose settings as a DQL data object
- Without security contexts, there's no data-level segmentation — all data is accessible to all users with tenant access
- Environment separation (prod/dev) is a compliance requirement in many industries

### Recommendations
1. **Verify API token scopes** — ensure `settings.read` and `settings.write` are granted
2. **Check security context configuration manually** in Settings → Security Context
3. **Define security contexts for environment separation** if mixing prod/dev data in the same tenant
4. **Consider separate tenants** for production vs. non-production if compliance requires strict isolation

### Next Steps
- Check API token scopes in Settings → Access Tokens (effort: 5 min)
- Review security context settings in Dynatrace UI (effort: 10 min)
- If no contexts exist, design a context strategy based on compliance requirements (effort: 1 hour)
- Implement contexts and validate data segmentation (effort: 2 hours, requires change window)
