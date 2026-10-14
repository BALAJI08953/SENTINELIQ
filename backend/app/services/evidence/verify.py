"""Evidence traceability and automated assessment.

Text match is kept separate from provenance, accessibility, corroboration, and
truth. None of these automated checks alone proves a claim.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, Observation, Source


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


def assess_evidence(db: Session, event: Event) -> list[dict]:
    assessments = []
    for evidence in event.evidence:
        observation = db.get(Observation, evidence.observation_id)
        source = db.get(Source, observation.source_id) if observation else None
        text_match = bool(observation and evidence.excerpt and evidence.excerpt.strip() in observation.body)
        urls = set()
        if observation:
            urls = {
                row[0] for row in db.execute(
                    select(Observation.url).where(
                        Observation.company_id == event.company_id,
                        Observation.url.is_not(None),
                    )
                ).all()
            }
        assessments.append({
            "evidence_id": evidence.id,
            "observation_id": evidence.observation_id,
            "text_match": text_match,
            "provenance": bool(observation and source),
            "source_accessible": bool(source and source.last_status == "ok"),
            "claim_consistency": "automated_text_support" if text_match else "unsupported_by_stored_text",
            "corroboration": "available" if len(urls) > 1 else "unavailable",
            "conflicting_evidence": False,
            "verification_status": evidence.verification_status,
            "limitation": "Automated assessment; does not establish that the underlying claim is true.",
        })
    return assessments
