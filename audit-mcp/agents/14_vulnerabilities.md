# Agent 14: Security & Vulnerabilities

**Category:** security
**Blast Radius:** CRITICAL / HIGH

## Purpose

Assess the security posture of the monitored environment by analyzing runtime vulnerabilities detected by Dynatrace Application Security.

## MCP Tools

### Tool 1: Active vulnerabilities

```tool
list_vulnerabilities(riskScore=1, timeframe="30d", maxVulnerabilitiesToDisplay=25)
```

### Tool 2: Critical vulnerabilities only

```tool
list_vulnerabilities(riskScore=8, timeframe="30d", maxVulnerabilitiesToDisplay=10)
```

## Checks

### Check: appsec_active
- **Per entity:** TENANT
- **PASS:** Vulnerability data is returned (even if 0 vulns — means AppSec is active)
- **INFO:** No vulnerability data available (AppSec may not be enabled)
- **Blast Radius:** HIGH
- **Remediation:** "Enable Dynatrace Application Security for runtime vulnerability detection"

### Check: critical_vulnerabilities
- **Per entity:** TENANT
- **PASS:** 0 critical vulnerabilities (risk score >= 8)
- **WARN:** 1-5 critical vulnerabilities
- **FAIL:** > 5 critical vulnerabilities
- **Blast Radius:** CRITICAL
- **Remediation:** "Found {count} critical vulnerabilities (risk >= 8) — prioritize remediation immediately"

### Check: total_vulnerabilities
- **Per entity:** TENANT
- **PASS:** < 10 total vulnerabilities
- **WARN:** 10-50 vulnerabilities
- **FAIL:** > 50 vulnerabilities
- **Blast Radius:** HIGH
- **Remediation:** "Found {count} total vulnerabilities — establish a vulnerability management process"

## Evaluation Notes

Dynatrace Application Security provides runtime vulnerability analysis. If `list_vulnerabilities` returns data (even empty), AppSec is enabled. If the tool returns an error or no-data message, AppSec may not be licensed or enabled.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- Zero vulnerabilities: either the environment runs minimal code (infrastructure-only), uses up-to-date dependencies, or the workloads don't match AppSec's code-level analysis targets (e.g., no Java/.NET/Node.js processes)
- AppSec active with no findings is a positive signal — the scanning infrastructure works and no known CVEs match runtime libraries
- If AppSec is NOT active: likely not licensed or not enabled in tenant settings

### Recommendations
1. **Maintain current posture** — continue monitoring with AppSec enabled
2. **Enable runtime vulnerability analytics** if not active — it's included in many Dynatrace licenses
3. **Set up vulnerability notification rules** — get alerted when new critical CVEs are detected
4. **Review third-party library inventory** periodically — even if no CVEs today, new ones are published daily
5. **Integrate with CI/CD pipeline** — use Dynatrace security gates to block deployments with critical vulnerabilities

### Next Steps
- Verify AppSec is enabled in Settings → Application Security (effort: 5 min)
- Configure vulnerability alerting for risk score >= 8 (effort: 10 min)
- Review the vulnerability inventory in Security → Vulnerabilities (effort: 15 min)
- Document security scanning baseline for future audits (effort: 15 min)
