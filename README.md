> 🇪🇸 [Leer en español](README.es.md)

# Observability Auditor

Automated Dynatrace observability maturity assessment with scoring, AI analysis, and interactive reports.

---

## What Is This

Two implementations of the same concept: audit a Dynatrace tenant's observability maturity automatically. Both produce a 0-100 maturity score across 5 categories, with detailed findings and AI-powered remediation recommendations.

This project was built for the **Dynatrace Observability Challenge 2025**.

---

## Two Approaches

| | audit-api | audit-mcp |
|---|---|---|
| **Approach** | Python CLI tool | Claude Code playbook |
| **How it runs** | `python -m src.cli run` | Claude Code + Dynatrace MCP Server |
| **Agents** | 12 async Python agents | 15 markdown-defined agents |
| **AI Analysis** | Claude API (programmatic) | Claude (native reasoning) |
| **Report** | Interactive HTML | Interactive HTML |
| **Best for** | CI/CD integration, automation | Interactive audits, deep exploration |

Each approach has its own directory with a detailed README:

- [`audit-api/`](audit-api/) — Python CLI implementation
- [`audit-mcp/`](audit-mcp/) — Claude Code MCP playbook

---

## How Scoring Works

- Each agent produces findings with status: **PASS**, **WARN**, or **FAIL**
- Findings are weighted by **blast_radius**: host (1.0) > service (0.8) > application (0.6) > config (0.4)
- Agent score = weighted pass rate (0-100)
- Global score = average of all agent scores
- Maturity semaphore: **GREEN** (>= 80), **YELLOW** (>= 50), **RED** (< 50)

---

## Audit Categories

| Category | What it covers |
|---|---|
| Infrastructure | OneAgent deployment, ActiveGate, host groups |
| Configuration | Management zones, tagging, ownership |
| Digital Experience | RUM, synthetic monitors |
| Operations | Anomaly detection, problem notifications, SLOs, problem history |
| Security | Security settings, vulnerability detection, Kubernetes |

---

## Sample Report

```
=== AUDIT COMPLETE ===
Tenant: Production (abc12345)
Global Score: 62/100 [YELLOW]

Category Scores:
  Infrastructure: 75/100
  Configuration:  45/100
  DEM:            50/100
  Operations:     70/100
  Security:       80/100

Findings: 47 (5 critical, 12 high, 30 medium)
```

---

## Built With

- Python 3.12 + asyncio
- Claude AI (Anthropic)
- Dynatrace API v2
- Dynatrace MCP Server (`@dynatrace-oss/dynatrace-mcp-server`)
- Jinja2 + HTML/CSS

---

## Getting Started

This is a monorepo. Each sub-project is self-contained with its own dependencies and setup instructions:

- For the Python CLI: see [audit-api/README.md](audit-api/README.md)
- For the MCP playbook: see [audit-mcp/README.md](audit-mcp/README.md)

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

**Alan Fuentes**
