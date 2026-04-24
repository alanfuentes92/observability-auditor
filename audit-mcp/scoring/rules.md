# Scoring Rules — Observability Audit

## Finding Structure

Each finding has these fields:

| Field | Description |
|-------|------------|
| check | Identifier for the check (e.g., `host_monitoring_enabled`) |
| entity_id | Dynatrace entity ID or "TENANT" for tenant-level checks |
| entity_name | Human-readable name |
| status | PASS, WARN, FAIL, or INFO |
| blast_radius | CRITICAL, HIGH, MEDIUM, or LOW |
| detail | Description of what was found |
| remediation | Recommended action to fix |

## Blast Radius Weights

| Blast Radius | Weight |
|-------------|--------|
| CRITICAL | 4.0 |
| HIGH | 3.0 |
| MEDIUM | 2.0 |
| LOW | 1.0 |

## Score Calculation — Per Agent

For each agent, collect all findings and calculate:

1. For each finding, get its weight from blast_radius
2. Calculate earned weight based on status:
   - **PASS** → 100% of weight (full credit)
   - **WARN** → 50% of weight (half credit)
   - **FAIL** → 0% of weight (no credit)
   - **INFO** → 0% of weight (informational, no penalty — excluded from total_weight too)
3. Sum `total_weight` (excluding INFO findings)
4. Sum `earned_weight`
5. **Agent score = (earned_weight / total_weight) × 100**, rounded to 1 decimal

If an agent has no findings (data unavailable via DQL), score = 0.0 and note it as "data not available".

## Score Calculation — Global

**Global score = average of all agent scores**, rounded to 1 decimal.

If an agent returned no data (score 0.0 due to data unavailability), exclude it from the average and note it in the report.

## Semaphore

| Score Range | Semaphore | Meaning |
|------------|-----------|---------|
| ≥ 85 | 🟢 GREEN | Good observability posture |
| ≥ 55 | 🟡 YELLOW | Needs improvement |
| < 55 | 🔴 RED | Critical gaps |

## Category Scores

Group agents by category and average their scores:

| Category | Agents |
|----------|--------|
| infrastructure | oneagent_activegate, host_groups, kubernetes |
| configuration | management_zones, auto_tags, manual_tags, ownership, security_context, anomaly_detection, problem_notifications, slos |
| dem | rum, synthetic_monitors |
| operations | problem_history |
| security | vulnerabilities |
