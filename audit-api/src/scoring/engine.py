from src.models import AuditResult, CheckStatus, Finding


class ScoringEngine:
    @staticmethod
    def calculate_agent_score(findings: list[Finding]) -> float:
        if not findings:
            return 0.0
        total_weight = 0.0
        earned_weight = 0.0
        for f in findings:
            w = f.blast_radius.weight
            total_weight += w
            if f.status == CheckStatus.PASS:
                earned_weight += w
            elif f.status == CheckStatus.WARN:
                earned_weight += w * 0.5
        if total_weight == 0:
            return 0.0
        return round((earned_weight / total_weight) * 100, 1)

    @staticmethod
    def calculate_global_score(results: list[AuditResult]) -> float:
        if not results:
            return 0.0
        return round(sum(r.score for r in results) / len(results), 1)

    @staticmethod
    def category_scores(results: list[AuditResult]) -> dict[str, float]:
        cats: dict[str, list[float]] = {}
        for r in results:
            cats.setdefault(r.category, []).append(r.score)
        return {cat: round(sum(s) / len(s), 1) for cat, s in cats.items()}

    @staticmethod
    def semaphore(score: float) -> str:
        if score >= 85:
            return "green"
        if score >= 55:
            return "yellow"
        return "red"
