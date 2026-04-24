from dataclasses import dataclass
from enum import Enum


class CheckStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    INFO = "info"

    @property
    def emoji(self) -> str:
        return {"pass": "\U0001f7e2", "warn": "\U0001f7e1", "fail": "\U0001f534", "info": "\U0001f535"}[self.value]


class BlastRadius(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def weight(self) -> float:
        return {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}[self.value]


@dataclass
class Finding:
    entity_id: str
    entity_name: str
    check: str
    status: CheckStatus
    detail: str
    remediation: str
    blast_radius: BlastRadius


@dataclass
class AuditResult:
    agent_name: str
    category: str
    findings: list[Finding]
    score: float
    summary: dict
    raw_data: dict
    duration_ms: int
