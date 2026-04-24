# Agent 01: OneAgent &amp; ActiveGate

**Category:** infrastructure
**Blast Radius:** CRITICAL / HIGH

## Purpose

Verify that all hosts have OneAgent installed in FULL_STACK mode, are in RUNNING state, and that ActiveGates are connected.

## DQL Queries

### Query 1: Host monitoring status

```dql
fetch dt.entity.host
| fields id, entity.name, state, monitoringMode, oneAgentVersion = toString(softwareTechnologies)
| limit 500
```

### Query 2: ActiveGate status

```dql
fetch dt.entity.environment_active_gate
| fields id, entity.name, networkAddresses, version
| limit 100
```

## Checks

### Check: host_monitoring_enabled
- **Per entity:** Each host
- **PASS:** monitoringMode == "FULL_STACK"
- **FAIL:** monitoringMode != "FULL_STACK" or missing
- **Blast Radius:** CRITICAL
- **Remediation:** "Set monitoring mode to FULL_STACK for host '{entity.name}'"

### Check: oneagent_installed
- **Per entity:** Each host
- **PASS:** oneAgentVersion is non-empty / non-null
- **FAIL:** No version detected
- **Blast Radius:** CRITICAL
- **Remediation:** "Install OneAgent on host '{entity.name}'"

### Check: host_state_running
- **Per entity:** Each host
- **PASS:** state == "RUNNING"
- **WARN:** state != "RUNNING"
- **Blast Radius:** HIGH
- **Remediation:** "Investigate host '{entity.name}' — state is '{state}'"

### Check: activegate_connected
- **Per entity:** Each ActiveGate
- **PASS:** Entity exists and has networkAddresses
- **FAIL:** Entity has no network addresses (unreachable)
- **Blast Radius:** CRITICAL
- **Remediation:** "Check ActiveGate '{entity.name}' process and network connectivity"

### Check: activegate_exists
- **Per entity:** TENANT
- **PASS:** At least one ActiveGate found
- **WARN:** No ActiveGates found
- **Blast Radius:** HIGH
- **Remediation:** "Consider deploying an ActiveGate for Environment or Cluster mode"

## DQL Fallback

If `dt.entity.environment_active_gate` is not available, try:

```dql
fetch dt.entity.active_gate
| fields id, entity.name, networkAddresses
| limit 100
```

If neither works, register an INFO finding: "ActiveGate data not available via DQL".

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- Hosts without OneAgent version: likely monitored via cloud integration (Kubernetes, AWS, etc.) rather than native agent — limited depth (no code-level visibility, no deep process monitoring)
- Missing ActiveGates: common in small/lab environments but limits extension capabilities, routing control, and multi-environment architecture

### Recommendations
1. **Verify OneAgent deployment method** for hosts showing null version — if cloud-only, consider installing native OneAgent for full-stack visibility
2. **Deploy at least one ActiveGate** if the environment has >5 hosts or requires private synthetic locations, extensions, or multi-environment routing
3. **Check OneAgent auto-update policy** — ensure agents stay current to receive latest security patches and features

### Next Steps
- Verify each host's monitoring method in Dynatrace UI → Hosts → [host] → Properties (effort: 5 min)
- Install OneAgent on hosts missing it via deployment page (effort: 15 min per host)
- Evaluate ActiveGate need based on environment growth plans (effort: 30 min planning)
