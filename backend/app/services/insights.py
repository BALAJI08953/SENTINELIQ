from sqlalchemy.orm import Session, selectinload

from app.models import Event, Observation
from app.services.companies import NotFoundError
from app.services.evidence.verify import assess_evidence


def _event(db: Session, event_id: int) -> Event:
    event = db.get(
        Event,
        event_id,
        options=[
            selectinload(Event.evidence),
            selectinload(Event.predictions),
            selectinload(Event.risk_assessments),
        ],
    )
    if not event:
        raise NotFoundError(f"Event {event_id} not found")
    return event


def build_event_insight(db: Session, event_id: int) -> dict:
    event = _event(db, event_id)
    observations = [db.get(Observation, evidence.observation_id) for evidence in event.evidence]
    observations = [obs for obs in observations if obs is not None]
    latest_prediction = max(event.predictions, key=lambda row: row.id, default=None)
    latest_risk = max(event.risk_assessments, key=lambda row: row.id, default=None)
    facts = [
        {
            "observation_id": obs.id,
            "title": obs.title,
            "source_url": obs.url,
            "excerpt": next((ev.excerpt for ev in event.evidence if ev.observation_id == obs.id), None),
        }
        for obs in observations
    ]
    implications = [
        "Review whether this change affects current positioning, pricing, sales enablement, or roadmap assumptions.",
        "Compare the source evidence with first-party knowledge before treating the event as confirmed.",
    ]
    if latest_risk and latest_risk.priority in {"high", "critical"}:
        implications.insert(0, "Prioritize human review because the current heuristic score is elevated.")
    return {
        "event_id": event.id,
        "summary": f"{event.title} is stored as a {event.category} event for company #{event.company_id}.",
        "source_facts": facts,
        "evidence_assessments": assess_evidence(db, event),
        "model_signal": None if latest_prediction is None else {
            "label": latest_prediction.label,
            "confidence": latest_prediction.confidence,
            "model_version": latest_prediction.model_version,
        },
        "risk_signal": None if latest_risk is None else {
            "priority": latest_risk.priority,
            "overall_score": latest_risk.overall_score,
            "explanation": latest_risk.explanation,
        },
        "possible_implications": implications,
        "uncertainties": [
            "Stored evidence proves traceability, not real-world truth.",
            "The deterministic local insight provider does not use external context.",
        ],
        "missing_information": [
            "Independent confirmation from additional sources.",
            "Business impact specific to your customer segments, pipeline, and product strategy.",
        ],
        "suggested_actions": [
            "Assign a human reviewer.",
            "Collect one additional source if the event is important.",
            "Record feedback after review so future training data can improve.",
        ],
        "provider": "deterministic_local",
    }


def build_decision_options(db: Session, event_id: int) -> dict:
    event = _event(db, event_id)
    return {
        "event_id": event.id,
        "disclaimer": "Options are hypothetical decision-support prompts, not automatic recommendations.",
        "options": [
            {
                "name": "Monitor only",
                "benefits": ["Avoids overreacting to weak or unverified signals.", "Keeps effort low."],
                "drawbacks": ["May miss a fast-moving competitor change."],
                "assumptions": ["Risk remains low or evidence is incomplete."],
                "next_steps": ["Set status to reviewed.", "Collect another source if the event recurs."],
            },
            {
                "name": "Sales enablement note",
                "benefits": ["Prepares customer-facing teams with sourced context."],
                "drawbacks": ["Can amplify unverified claims if caveats are omitted."],
                "assumptions": ["The event may appear in active deals or customer questions."],
                "next_steps": ["Summarize only source-backed facts.", "Link evidence in the internal note."],
            },
            {
                "name": "Strategic review",
                "benefits": ["Creates space to evaluate pricing, roadmap, or positioning impact."],
                "drawbacks": ["Consumes leadership time and may be unnecessary for routine events."],
                "assumptions": ["Risk priority or strategic relevance is high enough to justify review."],
                "next_steps": ["Confirm the event with additional evidence.", "Document decisions and owners."],
            },
        ],
    }
