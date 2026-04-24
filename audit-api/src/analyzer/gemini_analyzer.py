import json
from src.client.gemini import GeminiClient
from src.models import AuditResult
from src.scoring.engine import ScoringEngine


SECTION_PROMPT = """Sos un SRE senior especializado en Dynatrace. Analizá los siguientes resultados de auditoría del área "{agent_name}" para el tenant {tenant_url}.

## Datos de Auditoría
Score: {score}/100 ({semaphore})
Total checks: {total}, Passed: {passed}, Failed: {failed}, Warned: {warned}

## Findings Detallados
{findings_json}

Generá:
1. **ANÁLISIS**: Descripción del estado actual y su impacto operativo (200-400 palabras, español)
2. **RECOMENDACIONES**: Lista priorizada de acciones, ordenada por blast_radius (critical first)
3. **QUICK WINS**: Mejoras implementables en menos de 1 hora
4. **RIESGO**: Qué podría pasar en un incidente real si esto no se corrige

Formato: Markdown con headers ##. Tono profesional, directo, orientado a acción.
"""

EXECUTIVE_PROMPT = """Sos un SRE senior generando el resumen ejecutivo de una auditoría de observabilidad Dynatrace para el tenant {tenant_url}.

## Scores por Área
{category_scores}

## Score Global: {global_score}/100 ({global_semaphore})

## Resumen por Agente
{agent_summaries}

Generá un RESUMEN EJECUTIVO profesional en español:
1. **ESTADO GENERAL**: Evaluación en 2-3 oraciones del nivel de madurez de observabilidad
2. **TOP 5 HALLAZGOS CRÍTICOS**: Los 5 problemas más urgentes con su impacto
3. **ROADMAP DE REMEDIACIÓN**: Plan priorizado en 3 fases (inmediato <1 semana, corto plazo <1 mes, medio plazo <3 meses)
4. **RISK MATRIX**: Tabla de probabilidad × impacto para los gaps principales
5. **MÉTRICAS CLAVE**: KPIs que el equipo debería trackear post-remediación

Formato: Markdown profesional. Tono ejecutivo pero técnicamente preciso. 500-800 palabras.
"""


class GeminiAnalyzer:
    def __init__(self, client: GeminiClient, tenant_url: str):
        self.client = client
        self.tenant_url = tenant_url

    async def analyze_section(self, result: AuditResult) -> str:
        findings_data = [
            {"entity": f.entity_name, "check": f.check, "status": f.status.value,
             "detail": f.detail, "remediation": f.remediation, "blast_radius": f.blast_radius.value}
            for f in result.findings
        ]
        prompt = SECTION_PROMPT.format(
            agent_name=result.agent_name, tenant_url=self.tenant_url,
            score=result.score, semaphore=ScoringEngine.semaphore(result.score),
            total=result.summary.get("total", 0), passed=result.summary.get("passed", 0),
            failed=result.summary.get("failed", 0), warned=result.summary.get("warned", 0),
            findings_json=json.dumps(findings_data, indent=2, ensure_ascii=False),
        )
        return await self.client.generate(prompt)

    async def analyze_executive(self, results: list[AuditResult]) -> str:
        global_score = ScoringEngine.calculate_global_score(results)
        cat_scores = ScoringEngine.category_scores(results)
        agent_summaries = "\n".join(
            f"- **{r.agent_name}**: {r.score}/100 ({ScoringEngine.semaphore(r.score)}) — "
            f"{r.summary.get('passed', 0)} passed, {r.summary.get('failed', 0)} failed"
            for r in results
        )
        cat_text = "\n".join(
            f"- **{cat}**: {score}/100 ({ScoringEngine.semaphore(score)})" for cat, score in cat_scores.items()
        )
        prompt = EXECUTIVE_PROMPT.format(
            tenant_url=self.tenant_url, category_scores=cat_text,
            global_score=global_score, global_semaphore=ScoringEngine.semaphore(global_score),
            agent_summaries=agent_summaries,
        )
        return await self.client.generate(prompt)
