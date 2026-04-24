import base64
from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader
from src.models import AuditResult
from src.scoring.engine import ScoringEngine


def _md_to_html(text: str) -> str:
    """Convert markdown text to HTML."""
    if not text:
        return ""
    return markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])


class HTMLRenderer:
    def __init__(self):
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
        self.env.filters["semaphore"] = ScoringEngine.semaphore
        self.env.filters["semaphore_emoji"] = lambda s: {"green": "\U0001f7e2", "yellow": "\U0001f7e1", "red": "\U0001f534"}.get(ScoringEngine.semaphore(s), "\u26aa")
        self.env.filters["semaphore_color"] = lambda s: {"green": "#10b981", "yellow": "#f59e0b", "red": "#ef4444"}.get(ScoringEngine.semaphore(s), "#6b7280")
        self.env.filters["md"] = _md_to_html

    def _load_logo_base64(self) -> str:
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            return base64.b64encode(logo_path.read_bytes()).decode()
        return ""

    def render(self, results: list[AuditResult], analyses: dict[str, str],
               executive_summary: str, tenant_url: str, global_score: float,
               category_scores: dict[str, float]) -> str:
        template = self.env.get_template("report.html.j2")
        # Convert markdown analyses to HTML
        analyses_html = {k: _md_to_html(v) for k, v in analyses.items()}
        executive_html = _md_to_html(executive_summary)
        return template.render(
            results=results, analyses=analyses_html, executive_summary=executive_html,
            tenant_url=tenant_url, global_score=global_score, category_scores=category_scores,
            logo_base64=self._load_logo_base64(), semaphore=ScoringEngine.semaphore,
        )
