from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.predict import ModelNotAvailableError, classify_event, predict
from app.models import Event, MLPrediction, RiskAssessment
from app.services.evidence.verify import verify_event_evidence
from app.services.risk.assess import assess_event


@dataclass
class ProcessingResult:
    event_id: int
    evidence: dict[str, int]
    prediction_status: str
    risk_status: str
    error: str | None = None


IMPACT_BY_CATEGORY = {
    "pricing_change": 7.0,
    "product_launch": 7.0,
    "partnership": 6.0,
    "funding": 6.5,
    "leadership_change": 5.5,
    "regulatory_change": 8.0,
    "acquisition": 8.5,
    "expansion": 6.0,
    "other": 4.0,
}


def _urgency_for(event: Event) -> float:
    occurred_at = event.occurred_at
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=UTC)
    age_days = max(0, (datetime.now(UTC) - occurred_at).days)
    if age_days <= 1:
        return 8.0
    if age_days <= 7:
        return 6.5
    if age_days <= 30:
        return 5.0
    return 3.0


def classify_event_once(db: Session, event: Event) -> str:
    text = event.title.strip()
    if not text:
        return "skipped_empty_text"
    try:
        pred = predict(text)
    except ModelNotAvailableError:
        return "model_unavailable"
    exists = db.scalar(
        select(MLPrediction.id).where(
            MLPrediction.event_id == event.id,
            MLPrediction.model_version == pred.model_version,
            MLPrediction.label == pred.label,
        )
    )
    if exists:
        return "already_classified"
    classify_event(db, event)
    return "classified"


def assess_event_once(db: Session, event: Event) -> str:
    if db.scalar(select(RiskAssessment.id).where(RiskAssessment.event_id == event.id)):
        return "already_assessed"
    impact = IMPACT_BY_CATEGORY.get(event.category, IMPACT_BY_CATEGORY["other"])
    assess_event(db, event, impact=impact, urgency=_urgency_for(event), strategic_relevance=5.0)
    return "assessed"


def process_event_pipeline(
    db: Session, event: Event, allow_missing_model: bool = False
) -> ProcessingResult:
    evidence = verify_event_evidence(db, event)
    try:
        prediction_status = classify_event_once(db, event)
    except ModelNotAvailableError:
        if not allow_missing_model:
            raise
        prediction_status = "model_unavailable"
    db.refresh(event)
    risk_status = assess_event_once(db, event)
    return ProcessingResult(
        event_id=event.id,
        evidence=evidence,
        prediction_status=prediction_status,
        risk_status=risk_status,
    )


def process_events_pipeline(db: Session, events: list[Event]) -> list[ProcessingResult]:
    return [process_event_pipeline(db, event, allow_missing_model=True) for event in events]
