# Agent 11: Problem Notifications & Problem Health

**Category:** configuration
**Blast Radius:** CRITICAL / HIGH / MEDIUM

## Purpose

Verify that problem detection and notification infrastructure is working by analyzing problem history, custom alerts, and problem patterns.

## MCP Tools

### Tool 1: Problem history (30d)

```tool
list_problems(timeframe="30d", maxProblemsToDisplay=100)
```

Analyze problem categories, frequency, durations, and whether custom alerts exist (proves notification channels are configured).

### DQL Fallback: Problem events

```dql
fetch dt.davis.problems, from: now()-30d
| summarize count(), by: { event.category }
```

## Checks

### Check: problems_detected
- **Per entity:** TENANT
- **PASS:** At least one problem detected in last 30 days (Davis AI is active)
- **INFO:** No problems in 30 days (either very healthy or monitoring not active)
- **Blast Radius:** HIGH
- **Remediation:** "No problems detected in 30 days — verify Davis AI is enabled and monitoring is active"

### Check: custom_alerts_exist
- **Per entity:** TENANT
- **PASS:** At least one CUSTOM_ALERT category problem exists (proves notification/alerting rules are configured)
- **FAIL:** No custom alerts found — no alerting rules configured
- **Blast Radius:** CRITICAL
- **Remediation:** "Configure custom alerting rules — no CUSTOM_ALERT problems found in 30 days"

### Check: problem_mttr
- **Per entity:** TENANT
- **PASS:** Average problem duration < 4 hours (good MTTR)
- **WARN:** Average problem duration 4-24 hours
- **FAIL:** Average problem duration > 24 hours (problems linger too long)
- **Blast Radius:** HIGH
- **Remediation:** "Average problem duration is {avg_hours}h — investigate why problems take so long to resolve"

### Check: problem_noise_level
- **Per entity:** TENANT
- **PASS:** < 5 problems per day on average (manageable)
- **WARN:** 5-20 problems per day (noisy)
- **FAIL:** > 20 problems per day (alert fatigue risk)
- **Blast Radius:** MEDIUM
- **Remediation:** "Averaging {avg_per_day} problems/day — review alerting thresholds to reduce noise"

### Check: recurring_problem_pattern
- **Per entity:** TENANT
- **PASS:** No single entity generates > 50% of all problems
- **WARN:** One entity generates > 50% of problems (noisy host/service)
- **Blast Radius:** HIGH
- **Remediation:** "Entity '{entity_name}' generates {pct}% of all problems — investigate root cause or adjust thresholds"

## Evaluation Notes

This agent infers notification health from problem data. If CUSTOM_ALERT problems exist, it proves that alerting rules AND notification channels are configured (you can't have a CUSTOM_ALERT without both). Problem frequency and duration analysis adds operational maturity assessment beyond just "are notifications configured?"

## Analysis Guidelines

Structure the analysis as:

### Root Cause
- High problem noise (>20/day): often caused by one or two entities generating repetitive problems — investigate the dominant entity
- Slow MTTR: problems lingering >4h may indicate lack of on-call process, no automated remediation, or problems that auto-resolve and reoccur (flapping)
- Recurring pattern from single entity: typically an unstable host, misconfigured service, or network connectivity issue that keeps triggering/resolving

### Recommendations
1. **Investigate the top problem-generating entity** — fix the root cause rather than suppressing alerts
2. **Create alerting profiles with severity filters** — route critical problems immediately, batch low-severity for daily review
3. **Implement notification channel diversity** — at least email + Slack/Teams for redundancy
4. **Set up problem auto-close rules** for known transient issues while investigating root cause
5. **Establish an on-call rotation** if one doesn't exist — problems need owners, not just notifications

### Next Steps
- Identify the #1 problem-generating entity and investigate root cause (effort: 1 hour)
- Create at least 2 alerting profiles: "Critical" (immediate) and "Warning" (daily digest) (effort: 30 min)
- Add a second notification channel if only one exists (effort: 15 min)
- Review and mute known-flapping problems while fixing root cause (effort: 15 min)
- Document on-call escalation process (effort: 1 hour)
