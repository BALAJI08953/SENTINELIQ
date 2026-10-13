"""Evidence traceability checks. 'verified' means the cited text really exists in a stored
observation of the same company. It does NOT mean the underlying claim is true."""
from sqlalchemy.orm import Session

from app.models import Event, Observation


def check_reference(db: Session, event: Event, observation_id: int, url: str | None = None) -> bool:
    obs = db.get(Observation, observation_id)
    if obs is None or obs.company_id != event.company_id:
        return False
    return url is None or obs.url == url


def verify_event_evidence(db: Session, event: Event) -> dict[str, int]:
    counts = {"verified": 0, "unverified": 0}
    for ev in event.evidence:
        obs = db.get(Observation, ev.observation_id)
        ok = bool(obs and obs.company_id == event.company_id and ev.excerpt
                  and ev.excerpt.strip() and ev.excerpt.strip() in obs.body)
        ev.verification_status = "verified" if ok else "unverified"
        counts[ev.verification_status] += 1
    db.commit()
    return counts
