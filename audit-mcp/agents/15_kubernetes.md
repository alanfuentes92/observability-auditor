# Agent 15: Kubernetes Health

**Category:** infrastructure
**Blast Radius:** HIGH / MEDIUM

## Purpose

Assess Kubernetes cluster monitoring health by analyzing k8s events, pod readiness, and cluster visibility.

## MCP Tools

### Tool 1: Kubernetes events (7d)

```tool
get_kubernetes_events(timeframe="7d", maxEventsToDisplay=30)
```

### Tool 2: K8s workload entities

```dql
fetch dt.entity.cloud_application
| fields id, entity.name, tags
| limit 100
```

### Tool 3: K8s namespace entities

```dql
fetch dt.entity.cloud_application_namespace
| fields id, entity.name
| limit 100
```

## Checks

### Check: k8s_monitoring_active
- **Per entity:** TENANT
- **PASS:** Kubernetes entities (cloud_application or cloud_application_namespace) exist
- **INFO:** No Kubernetes entities found (k8s monitoring may not be configured)
- **Blast Radius:** HIGH
- **Remediation:** "Enable Kubernetes monitoring — deploy Dynatrace Operator for full k8s visibility"

### Check: k8s_pod_health
- **Per entity:** TENANT
- **PASS:** No ERROR_EVENT or "No pod ready" events in last 7 days
- **WARN:** 1-5 pod health events
- **FAIL:** > 5 pod health events (unstable workloads)
- **Blast Radius:** HIGH
- **Remediation:** "Found {count} pod health events in 7 days — investigate workload stability"

### Check: k8s_resource_events
- **Per entity:** TENANT
- **PASS:** No RESOURCE_CONTENTION_EVENT in last 7 days
- **WARN:** 1-3 resource contention events
- **FAIL:** > 3 resource contention events (cluster under-provisioned)
- **Blast Radius:** MEDIUM
- **Remediation:** "Found {count} resource contention events — review cluster resource allocation"

### Check: k8s_workload_tags
- **Per entity:** Each workload
- **PASS:** Workload has at least one tag
- **FAIL:** Workload has no tags
- **Blast Radius:** MEDIUM
- **Remediation:** "Apply tags to Kubernetes workload '{entity.name}'"

## Evaluation Notes

This agent combines entity queries with k8s-specific MCP tools. The `get_kubernetes_events` tool provides operational insights that aren't available through standard entity queries. If no k8s entities exist, all checks register as INFO (no penalty).

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- K8s availability events: clusters showing "Monitoring not available" often indicate Dynatrace Operator connectivity issues, expired tokens, or clusters that were registered but later decommissioned without cleanup
- Multiple cluster entities with ACTIVE availability problems: may be stale cluster registrations from previous deployments or test setups
- No workload tags: Kubernetes labels aren't being propagated as Dynatrace tags — auto-tagging rules for k8s metadata are missing
- Resource contention: pods requesting more resources than available, or nodes under-provisioned for the workload mix

### Recommendations
1. **Clean up stale cluster registrations** — remove cluster entities that no longer exist
2. **Verify Dynatrace Operator health** on active clusters — check operator pod logs and connection status
3. **Create auto-tag rules for Kubernetes metadata** — propagate namespace, workload name, and labels as Dynatrace tags
4. **Review resource requests/limits** for pods with contention events — right-size or add nodes
5. **Set up Kubernetes dashboards** in Dynatrace for cluster health visibility

### Next Steps
- Identify which k8s cluster entities are still active vs. stale (effort: 15 min)
- Delete stale cluster entities from Dynatrace (effort: 10 min)
- Check Dynatrace Operator pod status: `kubectl get pods -n dynatrace` (effort: 5 min)
- Create auto-tag rules for k8s.namespace.name and k8s.workload.name (effort: 15 min)
- Review resource contention events and adjust pod resource requests (effort: 1 hour)
