import asyncio
from src.agents import ALL_AGENTS
from src.client.dynatrace import DynatraceClient
from src.models import AuditResult


class Orchestrator:
    def __init__(self, client: DynatraceClient):
        self.client = client

    async def _run_agent(self, agent_cls) -> AuditResult:
        agent = agent_cls(self.client)
        try:
            return await agent.run()
        except Exception as e:
            return AuditResult(
                agent_name=getattr(agent, "name", agent_cls.__name__),
                category=getattr(agent, "category", "unknown"),
                findings=[], score=0.0,
                summary={"error": str(e)}, raw_data={}, duration_ms=0,
            )

    async def run_all(self) -> list[AuditResult]:
        tasks = [self._run_agent(cls) for cls in ALL_AGENTS]
        return list(await asyncio.gather(*tasks))
