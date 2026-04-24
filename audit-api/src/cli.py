import asyncio
import webbrowser

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import Settings
from src.client.dynatrace import DynatraceClient
from src.scoring.engine import ScoringEngine
from src.storage.history import HistoryStore

app = typer.Typer(name="audit", help="Dynatrace Observability Auditor")
console = Console()


@app.command()
def run(
    tenant_url: str = typer.Option(None, help="Dynatrace tenant URL"),
    api_token: str = typer.Option(None, help="Dynatrace API token"),
    gemini_key: str = typer.Option(None, help="Gemini API key"),
    no_ai: bool = typer.Option(False, help="Skip Gemini AI analysis"),
    open_report: bool = typer.Option(True, help="Open report in browser"),
):
    """Run a full observability audit."""
    settings = Settings(
        dt_tenant_url=tenant_url or "", dt_api_token=api_token or "",
        gemini_api_key=gemini_key or "",
    ) if tenant_url else Settings()
    asyncio.run(_run_audit(settings, no_ai, open_report))


async def _run_audit(settings: Settings, no_ai: bool, open_report: bool):
    from src.orchestrator import Orchestrator
    from src.client.gemini import GeminiClient
    from src.analyzer.gemini_analyzer import GeminiAnalyzer
    from src.renderer.html_renderer import HTMLRenderer

    dt_client = DynatraceClient(
        tenant_url=settings.env_api_url, api_token=settings.dt_api_token,
    )
    console.print(f"\n[bold]Auditing tenant:[/bold] {settings.dt_tenant_url}")
    console.print(f"[bold]Tenant ID:[/bold] {settings.tenant_id}\n")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Running 12 audit agents in parallel...", total=None)
        orch = Orchestrator(dt_client)
        results = await orch.run_all()
        progress.update(task, completed=True)

    table = Table(title="Audit Results")
    table.add_column("Agent", style="cyan")
    table.add_column("Category")
    table.add_column("Score", justify="right")
    table.add_column("Status")
    table.add_column("Findings", justify="right")
    table.add_column("Time (ms)", justify="right")
    for r in sorted(results, key=lambda x: x.score):
        sem = ScoringEngine.semaphore(r.score)
        emoji = {"green": "\U0001f7e2", "yellow": "\U0001f7e1", "red": "\U0001f534"}[sem]
        error = r.summary.get("error")
        score_text = f"{r.score:.1f}" if not error else "ERROR"
        table.add_row(r.agent_name, r.category, score_text, emoji,
                      str(r.summary.get("total", 0)), str(r.duration_ms))
    console.print(table)

    global_score = ScoringEngine.calculate_global_score(results)
    cat_scores = ScoringEngine.category_scores(results)
    sem = ScoringEngine.semaphore(global_score)
    emoji = {"green": "\U0001f7e2", "yellow": "\U0001f7e1", "red": "\U0001f534"}[sem]
    console.print(f"\n[bold]Global Score: {global_score:.1f}/100 {emoji}[/bold]\n")

    analyses = {}
    executive = ""
    if not no_ai:
        gemini_client = GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)
        analyzer = GeminiAnalyzer(client=gemini_client, tenant_url=settings.dt_tenant_url)
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Generating AI analysis...", total=len(results) + 1)
            for r in results:
                if not r.summary.get("error"):
                    analyses[r.agent_name] = await analyzer.analyze_section(r)
                progress.advance(task)
            executive = await analyzer.analyze_executive(results)
            progress.advance(task)
    else:
        console.print("[dim]Skipping AI analysis (--no-ai)[/dim]")

    renderer = HTMLRenderer()
    html = renderer.render(
        results=results, analyses=analyses, executive_summary=executive,
        tenant_url=settings.dt_tenant_url, global_score=global_score, category_scores=cat_scores,
    )

    store = HistoryStore(base_dir=settings.history_dir)
    run_id = store.save(settings.tenant_id, results, analyses, executive, html)
    report_path = store._run_dir(settings.tenant_id, run_id) / "report.html"
    console.print(f"[green]Report saved:[/green] {report_path}")

    # Also save to project output/ folder for easy access
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    local_report = output_dir / f"audit-report-{run_id}.html"
    local_report.write_text(html)
    console.print(f"[green]Local copy:[/green] {local_report}")

    if open_report:
        webbrowser.open(f"file://{local_report.resolve()}")
    await dt_client.close()


@app.command()
def history(
    tenant_url: str = typer.Option(None, help="Dynatrace tenant URL"),
    compare: str = typer.Option(None, help="Compare mode: 'last' or run_id"),
    open_report: str = typer.Option(None, help="Open a specific run's report"),
):
    """View audit history and compare runs."""
    settings = Settings() if not tenant_url else Settings(dt_tenant_url=tenant_url, dt_api_token="unused", gemini_api_key="unused")
    store = HistoryStore(base_dir=settings.history_dir)
    tenant_id = settings.tenant_id
    if open_report:
        path = store._run_dir(tenant_id, open_report) / "report.html"
        webbrowser.open(f"file://{path.resolve()}")
        return
    runs = store.list_runs(tenant_id)
    if not runs:
        console.print("[yellow]No audit history found.[/yellow]")
        return
    table = Table(title=f"Audit History \u2014 {tenant_id}")
    table.add_column("Run ID")
    table.add_column("Timestamp")
    table.add_column("Agents")
    for r in runs:
        agents = r.get("agents", {})
        avg_score = sum(a.get("score", 0) for a in agents.values()) / max(len(agents), 1)
        table.add_row(r["run_id"], r.get("timestamp", ""), f"{len(agents)} agents, avg {avg_score:.1f}")
    console.print(table)
    if compare == "last" and len(runs) >= 2:
        diff = store.compare(tenant_id, runs[1]["run_id"], runs[0]["run_id"])
        diff_table = Table(title="Score Comparison (previous \u2192 latest)")
        diff_table.add_column("Agent")
        diff_table.add_column("Before", justify="right")
        diff_table.add_column("After", justify="right")
        diff_table.add_column("Delta", justify="right")
        for agent, d in sorted(diff.items()):
            delta_str = f"+{d['delta']}" if d["delta"] > 0 else str(d["delta"])
            diff_table.add_row(agent, f"{d['before']:.1f}", f"{d['after']:.1f}", delta_str)
        console.print(diff_table)


@app.command()
def schedule(
    cron: str = typer.Option(None, help="Cron expression"),
    list_schedules: bool = typer.Option(False, "--list", help="List active schedules"),
):
    """Manage scheduled audits."""
    console.print("[yellow]Scheduler: coming in next iteration[/yellow]")


if __name__ == "__main__":
    app()
