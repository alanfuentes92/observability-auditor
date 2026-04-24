> 🇬🇧 [Read in English](README.md)

# Observability Auditor

Evaluacion automatizada de madurez de observabilidad en Dynatrace con scoring, analisis con IA y reportes interactivos.

---

## Que es esto

Dos implementaciones del mismo concepto: auditar automaticamente la madurez de observabilidad de un tenant de Dynatrace. Ambas producen un score de madurez de 0-100 en 5 categorias, con hallazgos detallados y recomendaciones de remediacion potenciadas por IA.

Este proyecto fue construido para el Dynatrace Observability Challenge 2025.

---

## Dos Enfoques

| | audit-api | audit-mcp |
|---|---|---|
| **Enfoque** | Herramienta CLI en Python | Playbook de Claude Code |
| **Ejecucion** | `python -m src.cli run` | Claude Code + Dynatrace MCP Server |
| **Agentes** | 12 agentes async en Python | 15 agentes definidos en markdown |
| **Analisis IA** | Claude API (programatico) | Claude (razonamiento nativo) |
| **Reporte** | HTML interactivo | HTML interactivo |
| **Ideal para** | Integracion CI/CD, automatizacion | Auditorias interactivas, exploracion profunda |

Cada enfoque tiene su propio directorio con un README detallado:

- [`audit-api/`](audit-api/) — Implementacion CLI en Python
- [`audit-mcp/`](audit-mcp/) — Playbook MCP para Claude Code

---

## Como Funciona el Scoring

- Cada agente produce hallazgos con estado: PASS, WARN, FAIL
- Los hallazgos se ponderan por blast_radius: host (1.0) > servicio (0.8) > aplicacion (0.6) > configuracion (0.4)
- Score por agente = tasa de aprobacion ponderada (0-100)
- Score global = promedio de scores de todos los agentes
- Semaforo de madurez: VERDE (>= 80), AMARILLO (>= 50), ROJO (< 50)

---

## Categorias de Auditoria

| Categoria | Que cubre |
|---|---|
| Infraestructura | Despliegue de OneAgent, ActiveGate, host groups |
| Configuracion | Management zones, tagging, ownership |
| Experiencia Digital | RUM, monitores sinteticos |
| Operaciones | Deteccion de anomalias, notificaciones de problemas, SLOs, historial |
| Seguridad | Configuracion de seguridad, deteccion de vulnerabilidades, Kubernetes |

---

## Ejemplo de Reporte

```
=== AUDITORIA COMPLETA ===
Tenant: Produccion (abc12345)
Score Global: 62/100 [AMARILLO]

Scores por Categoria:
  Infraestructura:      75/100
  Configuracion:        45/100
  Experiencia Digital:  50/100
  Operaciones:          70/100
  Seguridad:            80/100

Hallazgos: 47 (5 criticos, 12 altos, 30 medios)
```

---

## Construido Con

- Python 3.12 + asyncio
- Claude AI (Anthropic)
- Dynatrace API v2
- Dynatrace MCP Server (`@dynatrace-oss/dynatrace-mcp-server`)
- Jinja2 + HTML/CSS

---

## Como Empezar

- Para la CLI en Python: ver [audit-api/README.md](audit-api/README.md)
- Para el playbook MCP: ver [audit-mcp/README.md](audit-mcp/README.md)

---

## Licencia

MIT — ver [LICENSE](LICENSE)

---

## Autor

**Alan Fuentes**
