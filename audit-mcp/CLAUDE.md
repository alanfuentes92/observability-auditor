# CLAUDE.md — audit_mcp Playbook

## What This Is

A playbook for auditing Dynatrace tenant observability maturity using the Dynatrace MCP server. You (Claude) are the executor — read these instructions and follow them step by step.

## Prerequisites

1. The Dynatrace MCP server must be connected (configured via `.mcp.json` — see README)
2. The tenant credentials must be set in `.mcp.json` (DT_ENVIRONMENT and DT_AUTH_TOKEN)
3. Verify connectivity: call `get_environment_info` — if it fails, stop and troubleshoot

## How to Run an Audit

When the user says "auditá [tenant]" or "run audit", follow this sequence:

### Step 1: SETUP
1. Call `get_environment_info` to verify connectivity
2. Note the tenant ID, environment name, and version
3. Report: "Connected to tenant {id} — {name}. Starting audit."

### Step 2: COLLECT DATA (for each of the 15 agents)
1. Read the agent file from `agents/NN_name.md`
2. Execute each query or MCP tool call listed:
   - DQL queries → use `execute_dql`
   - MCP tools → use the corresponding tool directly (e.g., `list_problems`, `list_vulnerabilities`, `get_kubernetes_events`, `list_davis_analyzers`, `execute_davis_analyzer`)
3. If a query/tool fails, try the fallback if one exists
4. If all queries fail for an agent, register an INFO finding and move to the next agent
5. Save the raw results mentally — you'll need them for evaluation

### Step 3: EVALUATE (for each agent)
1. Apply each check defined in the agent file
2. For each check, determine the status (PASS/WARN/FAIL/INFO) based on the rules
3. Record each finding with: check, entity_id, entity_name, status, blast_radius, detail, remediation

### Step 4: CALCULATE SCORES
1. Read `scoring/rules.md`
2. For each agent, calculate the agent score using the formula
3. Calculate the global score (average of agent scores, excluding agents with no data)
4. Determine the semaphore color
5. Calculate category scores

### Step 5: SRE ANALYSIS
1. Identify the top 5 critical findings (FAIL with highest blast_radius)
2. Write an executive summary (3-5 paragraphs):
   - Overall maturity assessment
   - Critical gaps that need immediate attention
   - Quick wins (WARN findings easy to fix)
   - Strategic recommendations
3. For each agent, write a structured analysis following the template in the agent file's `## Analysis Guidelines` section. Every analysis MUST include:
   - **Root Cause:** Why is this happening? What's the underlying issue?
   - **Recommendations:** Specific, actionable items ordered by priority
   - **Next Steps:** Concrete tasks with effort estimates (e.g., "10 min", "1 hour", "requires change window")

### Step 6: GENERATE REPORT
1. Use the template in `templates/report.html` as CSS/structure reference
2. Generate a complete HTML file with:
   - Header: tenant name, ID, date, global score gauge
   - Score cards: per-agent scores with semaphore colors
   - Findings table: all findings grouped by agent, sorted by blast_radius
   - Executive summary section
   - Per-agent analysis sections
3. Write the file to `output/audit-report-{tenant_id}-{YYYY-MM-DD}.html`
4. Report the file path and key metrics to the user

## Output Format

When reporting results to the user, show:

```
=== AUDIT COMPLETE ===
Tenant: {name} ({tenant_id})
Global Score: {score}/100 [{semaphore}]

Category Scores:
  Infrastructure: {score}/100
  Configuration: {score}/100
  DEM: {score}/100
  Operations: {score}/100
  Security: {score}/100

Findings: {total} ({critical} critical, {high} high, {medium} medium)
Report: output/audit-report-{tenant_id}-{date}.html
```

## Important Notes

- Execute agents sequentially — don't try to parallelize DQL/MCP calls
- If rate-limited by the MCP server, wait and retry
- Always show the user what you're doing at each major step
- If a DQL query returns unexpected data, show the raw result and ask the user before proceeding
- Never skip an agent — if data is unavailable, register INFO findings
