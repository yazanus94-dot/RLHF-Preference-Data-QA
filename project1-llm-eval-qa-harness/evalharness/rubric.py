"""Rubric scoring: weighted checks, with 'critical' checks acting as hard gates."""
from dataclasses import dataclass, field
from typing import List

from .checks import CHECKS, CheckResult


@dataclass
class CheckSpec:
    type: str
    params: dict = field(default_factory=dict)
    weight: float = 1.0
    critical: bool = False


@dataclass
class Case:
    id: str
    category: str
    prompt: str
    checks: List[CheckSpec]
    pass_score: float = 0.8

    @classmethod
    def from_dict(cls, d: dict) -> "Case":
        specs = [CheckSpec(c["type"], c.get("params", {}), c.get("weight", 1.0), c.get("critical", False))
                 for c in d["checks"]]
        for s in specs:
            if s.type not in CHECKS:
                raise ValueError(f"case {d['id']}: unknown check type '{s.type}'")
        return cls(d["id"], d.get("category", "general"), d["prompt"], specs, d.get("pass_score", 0.8))


@dataclass
class ScoreResult:
    case_id: str
    score: float
    passed: bool
    critical_failed: bool
    results: List[CheckResult]


def score_response(response: str, case: Case) -> ScoreResult:
    results, earned, total, critical_failed = [], 0.0, 0.0, False
    for spec in case.checks:
        result = CHECKS[spec.type](response, spec.params)
        results.append(result)
        total += spec.weight
        if result.passed:
            earned += spec.weight
        elif spec.critical:
            critical_failed = True
    score = earned / total if total else 0.0
    passed = (score >= case.pass_score) and not critical_failed
    return ScoreResult(case.id, round(score, 4), passed, critical_failed, results)
