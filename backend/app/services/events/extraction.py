"""Turn observations into candidate events with linked evidence.

Category is left as 'other' here; the ML classifier (stage 3) assigns real categories.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, Evidence, Observation


def extract_event(db: Session, observation_id: int) -> Event | None:
    obs = db.get(Observation, observation_id)
    if obs is None:
        raise ValueError(f"Observation {observation_id} not found")
    if db.scalar(select(Evidence.id).where(Evidence.observation_id == obs.id)):
        return None  # already linked to an event
    ev = Event(company_id=obs.company_id, title=obs.title, category="other",
               occurred_at=obs.published_at or obs.collected_at, is_demo=obs.is_demo)
    db.add(ev)
    db.flush()
    db.add(Evidence(event_id=ev.id, observation_id=obs.id, excerpt=obs.body[:200],
                    verification_status="unverified"))
    db.commit()
    return ev


def extract_events(db: Session, observation_ids) -> list[Event]:
    return [e for oid in observation_ids if (e := extract_event(db, oid))]
