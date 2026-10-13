"""Transparent risk heuristic. A decision-support aid, NOT a validated loss prediction."""
from dataclasses import dataclass

WEIGHTS = {"impact": 0.35, "urgency": 0.25, "strategic_relevance": 0.25, "evidence_quality": 0.15}


@dataclass(frozen=True)
class RiskResult:
    impact: float
    urgency: float
    strategic_relevance: float
    evidence_quality: float
    overall_score: float
    priority: str
    explanation: str


def priority_for(score: float) -> str:
    if score < 35:
        return "low"
    if score < 60:
        return "medium"
    if score < 80:
        return "high"
    return "critical"


def score_risk(impact: float, urgency: float, strategic_relevance: float, evidence_quality: float) -> RiskResult:
    comps = {
        "impact": impact, "urgency": urgency,
        "strategic_relevance": strategic_relevance, "evidence_quality": evidence_quality,
    }
    for name, v in comps.items():
        if not 0 <= v <= 10:
            raise ValueError(f"{name} must be between 0 and 10, got {v}")
    overall = round(10 * sum(WEIGHTS[k] * v for k, v in comps.items()), 2)
    prio = priority_for(overall)
    parts = ", ".join(f"{k}={v:g} (w={WEIGHTS[k]:.0%})" for k, v in comps.items())
    explanation = f"overall={overall} -> {prio}. Components: {parts}. Heuristic only."
    return RiskResult(**comps, overall_score=overall, priority=prio, explanation=explanation)
