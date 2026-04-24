# Observability Auditor — MCP Edition

A Claude Code playbook that audits Dynatrace tenant observability maturity using the Dynatrace MCP server. No code to run — Claude is the executor.

---

## How It Works

1. Open Claude Code in this directory
2. Claude reads `CLAUDE.md` — the orchestration guide that defines the full audit workflow
3. Claude executes 15 agents sequentially, each querying Dynatrace via MCP tools:
   - `execute_dql` — DQL queries for entity state, metrics, and tags
   - `list_problems` — active and historical problem records
   - `list_vulnerabilities` — runtime vulnerability detection results
   - `get_kubernetes_events` — Kubernetes cluster events and workload health
   - `list_davis_analyzers` — anomaly detection analyzer configuration
   - `find_entity_by_name` — entity lookup for ownership and coverage checks
   - `chat_with_davis_copilot` — natural language Dynatrace queries
4. Each agent scores its findings by `blast_radius` weight
5. Claude generates an interactive HTML report and writes it to `output/`

No Python, no dependencies, no local server to start. Claude drives the entire audit through MCP.

---

## Prerequisites

- [Claude Code](https://claude.ai/code) — CLI, desktop app, or IDE extension
- Node.js 18+ (required by `npx` to run the Dynatrace MCP server — Claude handles this automatically)
- A Dynatrace tenant with a Platform token (OAuth or bearer)

The token must have access to:

- DQL query execution
- Problems API (read)
- Vulnerabilities API (read)
- Kubernetes events (read)
- Davis analyzers (read)
- Entity API (read)

---

## Quick Start

```bash
# 1. Clone the repository and enter the playbook directory
git clone https://github.com/alanfuentes92/observability-auditor.git
cd observability-auditor/audit-mcp

# 2. Create the MCP configuration file
cp mcp-config.example.json .mcp.json

# 3. Edit .mcp.json and replace the placeholders with your real values:
#    - DT_ENVIRONMENT: your Dynatrace Platform URL (e.g. https://abc123.apps.dynatrace.com)
#    - DT_AUTH_TOKEN: your Dynatrace Platform token

# 4. Open Claude Code in this directory
claude .

# 5. Tell Claude to run the audit
```

Inside Claude Code, say:

```
audit this tenant
```

or in Spanish:

```
auditá este tenant
```

Claude reads `CLAUDE.md` (the orchestration guide), detects the Dynatrace MCP server from `.mcp.json`, and runs the full 15-agent audit automatically. The HTML report is written to `output/`.

**Why `.mcp.json` and not `.env`?** Claude Code does not load `.env` files. The `.mcp.json` file is how Claude Code discovers and configures MCP servers. It contains your credentials, which is why it is gitignored — your secrets never leave your machine.

---

## Configuration

Copy `mcp-config.example.json` to `.mcp.json` and fill in your credentials:

```bash
cp mcp-config.example.json .mcp.json
```

Then edit `.mcp.json`:

| Field | Description | Example |
|---|---|---|
| `DT_ENVIRONMENT` | Dynatrace Platform URL | `https://abc123.apps.dynatrace.com` |
| `DT_AUTH_TOKEN` | Platform bearer or OAuth token | `dt0s16.XXXX.YYYY` |

**How to get a token:** In your Dynatrace tenant, go to **Access Tokens** and create a token with scopes: `storage:events:read`, `storage:entities:read`, `problems:read`, `securityProblems:read`, `slo:read`, `ReadSyntheticData`, `entities:read`, `settings:read`.

The `.mcp.json` file is gitignored — your credentials stay local and are never committed.

---

## Agents

The audit runs 15 agents in sequence. Each agent is defined as a markdown file in `agents/` containing its queries, checks, scoring rules, and analysis guidelines.

| # | Agent | Audits |
|---|---|---|
| 01 | OneAgent & ActiveGate | Deployment coverage, version compliance, ActiveGate presence |
| 02 | Host Groups | Host group organization and assignment |
| 03 | Management Zones | Access control and data segmentation rules |
| 04 | Auto Tags | Automatic tagging rule coverage |
| 05 | Manual Tags | Manual tag hygiene across entities |
| 06 | Ownership | Entity ownership assignment via `dt.owner` |
| 07 | Security Context | Security settings, vulnerability detection configuration |
| 08 | RUM | Real User Monitoring application configuration |
| 09 | Synthetic Monitors | Synthetic test coverage and health |
| 10 | Anomaly Detection | Davis AI analyzers and custom detection rules |
| 11 | Problem Notifications | Alerting integrations and notification setup |
| 12 | SLOs | Service Level Objectives definition and burn rate |
| 13 | Problem History | 30-day problem trends, MTTR, recurrence patterns |
| 14 | Vulnerabilities | Runtime vulnerability detection and remediation status |
| 15 | Kubernetes | K8s cluster monitoring, workload coverage, events |

---

## Scoring

Each agent produces findings with one of four statuses:

| Status | Meaning |
|---|---|
| `PASS` | Control is in place and healthy |
| `WARN` | Partial coverage or configuration gap |
| `FAIL` | Missing or broken — requires attention |
| `INFO` | Informational — no score impact |

Findings are weighted by `blast_radius` — the scope of impact if this control is missing:

| Scope | Weight |
|---|---|
| host | 1.0 |
| service | 0.8 |
| application | 0.6 |
| config | 0.4 |

**Agent score** = weighted average of findings (0–100)

**Global score** = average of all agent scores (agents with no data are excluded)

**Semaphore thresholds:**

- GREEN: score >= 80
- YELLOW: score >= 50
- RED: score < 50

---

## Project Structure

```
audit-mcp/
├── CLAUDE.md           # Orchestration guide — Claude reads this to run the audit
├── mcp-config.example.json  # MCP config template (copy to .mcp.json)
├── .env.example        # Environment variable template
├── agents/             # 15 markdown-defined audit agents
│   ├── 01_oneagent_activegate.md
│   ├── 02_host_groups.md
│   ├── 03_management_zones.md
│   ├── 04_auto_tags.md
│   ├── 05_manual_tags.md
│   ├── 06_ownership.md
│   ├── 07_security_context.md
│   ├── 08_rum.md
│   ├── 09_synthetic_monitors.md
│   ├── 10_anomaly_detection.md
│   ├── 11_problem_notifications.md
│   ├── 12_slos.md
│   ├── 13_problem_history.md
│   ├── 14_vulnerabilities.md
│   └── 15_kubernetes.md
├── scoring/
│   └── rules.md        # Scoring formula and weights
└── templates/
    └── report.html     # HTML report template
```

---

## Example Output

```
=== AUDIT COMPLETE ===
Tenant: My Tenant (abc12345)
Global Score: 36.6/100 [RED]

Category Scores:
  Infrastructure: 45/100
  Configuration:  20/100
  DEM:            15/100
  Operations:     55/100
  Security:       48/100

Findings: 63 (8 critical, 15 high, 40 medium)
Report: output/audit-report-abc12345-2026-04-24.html
```

The HTML report includes an executive summary, per-agent breakdowns, finding details with remediation guidance, and trend charts if historical data is available.

---

## Customization

**Add a new agent:** Create `agents/NN_name.md` following the structure of any existing agent file — include a Purpose section, DQL queries, check definitions, a Scoring section, and Analysis Guidelines.

**Modify scoring weights:** Edit `scoring/rules.md` to adjust `blast_radius` weights or score thresholds.

**Change the report appearance:** Edit `templates/report.html` — the template uses standard HTML/CSS with Jinja2-style placeholders that Claude fills in during report generation.

---

## License

MIT — see [LICENSE](../LICENSE)
