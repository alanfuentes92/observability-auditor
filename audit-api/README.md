# Observability Auditor — API Edition

Automated Dynatrace observability maturity auditor using Python async agents, weighted scoring, AI analysis, and interactive HTML reports.

---

## Architecture

```
CLI (Typer)
    │
    ▼
Orchestrator
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
12 Agents (parallel, async)          Scoring Engine
    │                                      │ (weighted by blast_radius)
    └──────────────┬───────────────────────┘
                   ▼
            AI Analyzer (Anthropic)
                   │
                   ▼
            HTML Renderer (Jinja2)
                   │
                   ▼
            audit-report.html + History Storage
```

**Blast radius weight order:** host > service > application > config

---

## Features

- 12 specialized audit agents running in parallel (async)
- Weighted scoring by blast_radius — infrastructure findings penalize more than config findings
- AI-powered analysis with root cause identification and remediation recommendations
- Interactive HTML report with responsive design
- Audit history with filesystem storage and diff/comparison between runs
- Scheduled audit runs via APScheduler

---

## Prerequisites

- **Python 3.12+**
- **Dynatrace tenant** with API v2 access token. Required scopes:
  - `entities.read`
  - `settings.read`
  - `problems.read`
  - `securityProblems.read`
  - `slo.read`
  - `syntheticExecution.read`
- **Anthropic API key** for AI-powered analysis

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/tracegazer/observability-auditor.git
cd observability-auditor/audit-api

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and fill in your credentials

# Run the audit
python -m src.cli run
```

---

## Configuration

All configuration is loaded from environment variables (or a `.env` file).

| Variable | Description | Required |
|---|---|---|
| `DT_TENANT_URL` | Dynatrace tenant URL (e.g. `https://abc123.live.dynatrace.com`) | Yes |
| `DT_API_TOKEN` | API v2 token with required scopes | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI analysis | Yes |
| `DT_OAUTH_CLIENT_ID` | OAuth client ID (Platform API) | No |
| `DT_OAUTH_CLIENT_SECRET` | OAuth client secret | No |
| `DT_OAUTH_SCOPE` | OAuth scope | No |

---

## Usage

```bash
# Run a full observability audit
python -m src.cli run

# List all past audit runs
python -m src.cli history list

# Compare two audit runs
python -m src.cli history compare
```

---

## Agents

The auditor runs 12 specialized agents in parallel. Each produces a score and a list of findings.

| # | Agent | Audits |
|---|---|---|
| 1 | OneAgent & ActiveGate | Deployment coverage and version compliance |
| 2 | Host Groups | Host group organization |
| 3 | Management Zones | Access control and data segmentation |
| 4 | Auto Tags | Automatic tagging rules |
| 5 | Manual Tags | Manual tag hygiene |
| 6 | Ownership | Entity ownership assignment |
| 7 | Security Context | Security settings and vulnerabilities |
| 8 | RUM | Real User Monitoring configuration |
| 9 | Synthetic Monitors | Synthetic test coverage |
| 10 | Anomaly Detection | Custom anomaly detection rules |
| 11 | Problem Notifications | Alerting and integration setup |
| 12 | SLOs | Service Level Objectives definition |

---

## Project Structure

```
audit-api/
├── pyproject.toml
├── .env.example
├── src/
│   ├── cli.py              # Typer CLI commands
│   ├── config.py           # Pydantic settings
│   ├── models.py           # Data models
│   ├── orchestrator.py     # Agent orchestration
│   ├── agents/             # 12 audit agents
│   ├── analyzer/           # AI analysis engine
│   ├── client/             # Dynatrace API client (httpx async)
│   ├── renderer/           # Jinja2 HTML report renderer
│   ├── scoring/            # Weighted scoring engine
│   └── storage/            # Audit history filesystem storage
└── tests/
```

---

## Example Output

```
=== AUDIT COMPLETE ===
Tenant: My Tenant (abc12345)
Global Score: 62/100 [🟡 YELLOW]

Category Scores:
  Infrastructure: 75/100
  Configuration:  45/100
  DEM:            50/100
  Operations:     70/100
  Security:       80/100

Findings: 47 (5 critical, 12 high, 30 medium)
Report: output/audit-report-abc12345-2026-04-24.html
```

---

## Development

```bash
# Run tests
python -m pytest tests/ -v

# Lint
ruff check src/ tests/

# Install with dev dependencies
pip install -e ".[dev]"
```

---

## License

MIT — see [LICENSE](../LICENSE)
