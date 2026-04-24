# Agent 10: Anomaly Detection

**Category:** configuration
**Blast Radius:** HIGH

## Purpose

Verify that anomaly detection is active and effective by analyzing Davis AI analyzer capabilities and recent anomaly-related problems.

## MCP Tools

### Tool 1: Davis Analyzers inventory

```tool
list_davis_analyzers
```

Lists all available Davis Analyzers (anomaly detection, forecast, etc.) — confirms the tenant has AI-powered detection capabilities.

### Tool 2: Recent anomaly problems (30d)

```tool
list_problems(timeframe="30d", maxProblemsToDisplay=50)
```

Filter results for categories: SLOWDOWN, RESOURCE_CONTENTION, ERROR — these indicate anomaly detection is firing.

### DQL Fallback: Host CPU anomaly check

```dql
timeseries avg_cpu = avg(dt.host.cpu.usage), by: { dt.entity.host }
| filter avg_cpu > 80
```

## Checks

### Check: davis_analyzers_available
- **Per entity:** TENANT
- **PASS:** At least 3 Davis Analyzers available (anomaly detection, forecast, baseline)
- **FAIL:** Fewer than 3 analyzers available
- **Blast Radius:** HIGH
- **Remediation:** "Verify Davis AI is enabled for this tenant — expected anomaly detection, forecast, and baseline analyzers"

### Check: anomaly_detection_firing
- **Per entity:** TENANT
- **PASS:** At least one SLOWDOWN or RESOURCE_CONTENTION problem detected in last 30 days (proves detection is active)
- **WARN:** No anomaly-based problems in 30 days (detection may not be tuned)
- **Blast Radius:** HIGH
- **Remediation:** "Review anomaly detection sensitivity — no anomaly-based problems detected in 30 days"

### Check: anomaly_problem_ratio
- **Per entity:** TENANT
- **PASS:** Anomaly-based problems (SLOWDOWN, ERROR, RESOURCE) represent < 60% of total problems (healthy balance)
- **WARN:** Anomaly-based problems represent >= 60% of total (may indicate noisy thresholds)
- **Blast Radius:** HIGH
- **Remediation:** "High ratio of anomaly-based problems ({pct}%) — review and tune detection thresholds to reduce noise"

## Evaluation Notes

This agent uses MCP tools instead of dt.setting queries. The key insight is: if Davis Analyzers exist AND anomaly-based problems are being generated, then anomaly detection is active and functional. The ratio check catches over-sensitive configurations that generate noise.

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- High anomaly ratio (>60%): Davis AI is detecting too many anomalies — likely default thresholds are too sensitive for this environment's baseline
- Default thresholds assume production workloads — lab/dev environments often have irregular traffic patterns that trigger false positives
- RESOURCE_CONTENTION events may indicate genuinely under-provisioned infrastructure OR overly sensitive resource thresholds

### Recommendations
1. **Tune anomaly detection thresholds** per host/service — adjust CPU, memory, response time baselines to match actual workload patterns
2. **Use custom thresholds for lab environments** — wider tolerance bands to reduce noise
3. **Review RESOURCE_CONTENTION events** — determine if they indicate real capacity issues or false positives
4. **Leverage Davis AI analyzers** for forecasting — use GenericForecastAnalyzer to predict capacity needs
5. **Consider muting non-critical hosts** during known maintenance/test windows

### Next Steps
- Review top 10 noisiest anomaly-generating entities (effort: 30 min)
- Adjust thresholds for lab hosts in Settings → Anomaly Detection (effort: 15 min per host)
- Set up maintenance windows for planned test activities (effort: 15 min)
- Run a forecast analysis on CPU/memory for capacity planning (effort: 30 min)
