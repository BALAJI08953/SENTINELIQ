from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import PageParams
from app.core.database import get_db
from app.ml.predict import classify_event
from app.models import Event, Feedback, Observation, RiskAssessment
from app.schemas import (
    EventDetail,
    EventOut,
    EventUpdate,
    FeedbackIn,
    FeedbackOut,
    ObservationOut,
    Page,
    RiskIn,
    RiskOut,
)
from app.services.companies import NotFoundError
from app.services.events.extraction import extract_event
from app.services.evidence.verify import verify_event_evidence
from app.services.risk.assess import assess_event

router = APIRouter(tags=["intelligence"])


def _page(db, stmt, p, schema):
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.offset(p.offset).limit(p.limit)).all()
    return Page(items=rows, total=total, offset=p.offset, limit=p.limit)


def _event(db: Session, event_id: int) -> Event:
    e = db.get(Event, event_id)
    if not e:
        raise NotFoundError(f"Event {event_id} not found")
    return e


@router.get("/observations", response_model=Page[ObservationOut])
def list_observations(company_id: int | None = None, q: str | None = None, is_demo: bool | None = None,
                      p: PageParams = Depends(), db: Session = Depends(get_db)):
    stmt = select(Observation)
    if company_id:
        stmt = stmt.where(Observation.company_id == company_id)
    if q:
        stmt = stmt.where(Observation.title.ilike(f"%{q}%") | Observation.body.ilike(f"%{q}%"))
    if is_demo is not None:
        stmt = stmt.where(Observation.is_demo == is_demo)
    return _page(db, stmt.order_by(Observation.collected_at.desc(), Observation.id.desc()), p, ObservationOut)


@router.get("/observations/{obs_id}", response_model=ObservationOut)
def get_observation(obs_id: int, db: Session = Depends(get_db)):
    o = db.get(Observation, obs_id)
    if not o:
        raise NotFoundError(f"Observation {obs_id} not found")
    return o


@router.post("/observations/{obs_id}/extract-event", response_model=EventOut, status_code=201)
def make_event(obs_id: int, db: Session = Depends(get_db)):
    ev = extract_event(db, obs_id)
    if ev is None:
        raise ValueError("Observation is already linked to an event")
    return ev


@router.get("/events", response_model=Page[EventOut])
def list_events(company_id: int | None = None, category: str | None = None, status: str | None = None,
                q: str | None = None, p: PageParams = Depends(), db: Session = Depends(get_db)):
    stmt = select(Event)
    if company_id:
        stmt = stmt.where(Event.company_id == company_id)
    if category:
        stmt = stmt.where(Event.category == category)
    if status:
        stmt = stmt.where(Event.status == status)
    if q:
        stmt = stmt.where(Event.title.ilike(f"%{q}%"))
    return _page(db, stmt.order_by(Event.occurred_at.desc(), Event.id.desc()), p, EventOut)


@router.get("/events/{event_id}", response_model=EventDetail)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return _event(db, event_id)


@router.patch("/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, body: EventUpdate, db: Session = Depends(get_db)):
    e = _event(db, event_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(e, k, v)
    db.commit()
    return e


@router.post("/events/{event_id}/process")
def process_event(event_id: int, db: Session = Depends(get_db)):
    """Classify with the trained model (503 if none) and verify evidence traceability."""
    e = _event(db, event_id)
    pred = classify_event(db, e)
    counts = verify_event_evidence(db, e)
    return {"prediction": {"label": pred.label, "confidence": pred.confidence,
                           "model_version": pred.model_version},
            "category": e.category, "evidence": counts}


@router.post("/events/{event_id}/risk", response_model=RiskOut, status_code=201)
def create_risk(event_id: int, body: RiskIn, db: Session = Depends(get_db)):
    return assess_event(db, _event(db, event_id), body.impact, body.urgency,
                        body.strategic_relevance, body.evidence_quality)


@router.get("/risk-assessments", response_model=Page[RiskOut])
def list_risk(priority: str | None = None, event_id: int | None = None, p: PageParams = Depends(),
              db: Session = Depends(get_db)):
    stmt = select(RiskAssessment)
    if priority:
        stmt = stmt.where(RiskAssessment.priority == priority)
    if event_id:
        stmt = stmt.where(RiskAssessment.event_id == event_id)
    return _page(db, stmt.order_by(RiskAssessment.overall_score.desc(), RiskAssessment.id), p, RiskOut)


@router.post("/events/{event_id}/feedback", response_model=FeedbackOut, status_code=201)
def add_feedback(event_id: int, body: FeedbackIn, db: Session = Depends(get_db)):
    _event(db, event_id)
    row = Feedback(event_id=event_id, **body.model_dump())
    db.add(row)
    db.commit()
    return row
