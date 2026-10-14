from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.insights import build_decision_options, build_event_insight

router = APIRouter(tags=["insights"])


@router.get("/events/{event_id}/insights")
def event_insights(event_id: int, db: Session = Depends(get_db)):
    return build_event_insight(db, event_id)


@router.get("/events/{event_id}/decision-support")
def event_decision_support(event_id: int, db: Session = Depends(get_db)):
    return build_decision_options(db, event_id)
