import time
from abc import ABC, abstractmethod
from src.client.dynatrace import DynatraceClient
from src.models import AuditResult, Finding
from src.scoring.engine import ScoringEngine


class BaseAuditAgent(ABC):
    name: str = "base"
    category: str = "configuration"

    def __init__(self, client: DynatraceClient):
        self.client = client

    @abstractmethod
    async def collect(self) -> dict:
        """Collect raw data from Dynatrace APIs."""

    @abstractmethod
    def analyze(self, data: dict) -> list[Finding]:
        """Analyze collected data and return findings."""

    async def run(self) -> AuditResult:
        start = time.perf_counter_ns()
        data = await self.collect()
        findings = self.analyze(data)
        score = ScoringEngine.calculate_agent_score(findings)
        duration_ms = (time.perf_counter_ns() - start) // 1_000_000
        passed = sum(1 for f in findings if f.status.value == "pass")
        failed = sum(1 for f in findings if f.status.value == "fail")
        warned = sum(1 for f in findings if f.status.value == "warn")
        return AuditResult(
            agent_name=self.name, category=self.category,
            findings=findings, score=score,
            summary={"total": len(findings), "passed": passed, "failed": failed, "warned": warned},
            raw_data=data, duration_ms=duration_ms,
        )
