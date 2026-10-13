from sqlalchemy.orm import Session

from app.models import Event, RiskAssessment
from app.services.risk.scoring import score_risk


def derive_evidence_quality(event: Event) -> float:
    """Heuristic 0-10: none=0; any evidence=4; +3 if any verified; +3 if >=2 distinct observations."""
    if not event.evidence:
        return 0.0
    q = 4.0
    if any(e.verification_status == "verified" for e in event.evidence):
        q += 3
    if len({e.observation_id for e in event.evidence}) >= 2:
        q += 3
    return q


def assess_event(db: Session, event: Event, impact: float, urgency: float,
                 strategic_relevance: float, evidence_quality: float | None = None) -> RiskAssessment:
    eq = derive_evidence_quality(event) if evidence_quality is None else evidence_quality
    r = score_risk(impact, urgency, strategic_relevance, eq)
    row = RiskAssessment(event_id=event.id, impact=r.impact, urgency=r.urgency,
                         strategic_relevance=r.strategic_relevance, evidence_quality=r.evidence_quality,
                         overall_score=r.overall_score, priority=r.priority, explanation=r.explanation)
    db.add(row)
    db.commit()
    return row
