"""Grounded SENTRIX retrieval and answer generation."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import requests
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.ml.experiments import get_experiment, list_experiments
from app.models import Company, Event, Observation, Source
from app.services.companies import NotFoundError


class SentrixProvider(Protocol):
    name: str

    def generate(self, message: str, context: dict[str, Any]) -> str: ...


class DeterministicProvider:
    name = "deterministic_grounded"

    def generate(self, message: str, context: dict[str, Any]) -> str:
        events = list(context["events"])
        companies = context["companies"]
        experiments = context["experiments"]
        if experiments:
            return _experiment_answer(experiments[0])
        if not events and not companies:
            return (
                "I could not find supporting SentinelIQ records for that question. "
                "Add a company, collect a permitted source, or select a specific event or experiment."
            )
        if any(phrase in message.casefold() for phrase in ("highest risk", "risk score", "most risky", "top risk")):
            events.sort(key=lambda event: (event.get("risk") or {}).get("overall_score", 0), reverse=True)
        lines: list[str] = []
        if companies:
            lines.append(f"I found {len(events)} event record(s) for {', '.join(c['name'] for c in companies)}.")
        if events:
            lines.append("Key findings:")
            for event in events[:8]:
                risk = event.get("risk")
                risk_text = f"; risk {risk['priority']} ({risk['overall_score']:.0f}/100)" if risk else ""
                lines.append(f"- {event['title']} ({event['category']}, {event['occurred_at'][:10]}){risk_text}.")
        if any(word in message.casefold() for word in ("why", "matter", "impact", "implication")):
            lines.append(
                "Interpretation: these records may matter for competitive positioning, but "
                "business impact is an inference and needs company-specific validation."
            )
        lines.append(
            "Evidence limitation: stored excerpts establish traceability and text match; "
            "they do not prove the underlying claim is true."
        )
        return "\n".join(lines)


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def generate(self, message: str, context: dict[str, Any]) -> str:
        if not settings.llm_base_url or not settings.llm_api_key or not settings.llm_model:
            raise RuntimeError("SENTINELIQ_LLM_BASE_URL, SENTINELIQ_LLM_API_KEY, and SENTINELIQ_LLM_MODEL are required")
        response = requests.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"},
            json={
                "model": settings.llm_model,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are SENTRIX, SentinelIQ's grounded competitive-intelligence assistant. "
                            "Use only supplied records. Mark inferences and say when evidence is insufficient. "
                            "Never invent URLs, metrics, events, or companies."
                        ),
                    },
                    {"role": "user", "content": json.dumps({"question": message, "records": context})},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


@dataclass
class SentrixResult:
    answer: str
    provider: str
    citations: list[dict[str, Any]]
    records: dict[str, Any]


def answer(
    db: Session,
    message: str,
    *,
    company_id: int | None = None,
    event_id: int | None = None,
    experiment_id: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> SentrixResult:
    if not message.strip():
        raise ValueError("message is required")
    companies = _companies(db, message, company_id)
    events = _events(db, message, companies, event_id, start, end)
    experiments = _experiments(experiment_id, message)
    context, citations = _context(db, companies, events, experiments)
    provider: SentrixProvider = DeterministicProvider()
    if settings.llm_provider.lower() not in {"", "deterministic", "none"}:
        provider = OpenAICompatibleProvider()
    try:
        text = provider.generate(message, context)
    except (RuntimeError, requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        provider = DeterministicProvider()
        text = provider.generate(message, context)
    return SentrixResult(text, provider.name, citations, {
        "companies": [c["id"] for c in context["companies"]],
        "events": [e["id"] for e in context["events"]],
        "experiments": [e["id"] for e in context["experiments"]],
    })


def _companies(db: Session, message: str, company_id: int | None) -> list[Company]:
    if company_id is not None:
        row = db.get(Company, company_id)
        if not row:
            raise NotFoundError(f"Company {company_id} not found")
        return [row]
    lowered = message.casefold()
    return [c for c in db.scalars(select(Company).order_by(Company.name)).all() if c.name.casefold() in lowered]


def _events(db: Session, message: str, companies: list[Company], event_id: int | None, start: datetime | None, end: datetime | None) -> list[Event]:
    stmt = select(Event).options(selectinload(Event.evidence), selectinload(Event.predictions), selectinload(Event.risk_assessments))
    if event_id is not None:
        stmt = stmt.where(Event.id == event_id)
    elif companies:
        stmt = stmt.where(Event.company_id.in_([c.id for c in companies]))
    if start:
        stmt = stmt.where(Event.occurred_at >= start)
    if end:
        stmt = stmt.where(Event.occurred_at <= end)
    if not event_id and not companies:
        terms = [term for term in message.casefold().split() if len(term) >= 4]
        broad_question = any(
            phrase in message.casefold()
            for phrase in (
                "latest",
                "development",
                "event",
                "risk",
                "highest",
                "overview",
                "summary",
                "summarize",
                "trend",
                "portfolio",
            )
        )
        if terms and not broad_question:
            stmt = stmt.where(or_(*[Event.title.ilike(f"%{term}%") for term in terms[:6]]))
    return db.scalars(stmt.order_by(Event.occurred_at.desc(), Event.id.desc()).limit(20)).all()


def _experiments(experiment_id: str | None, message: str) -> list[dict[str, Any]]:
    records = list_experiments()
    if experiment_id:
        return [get_experiment(experiment_id)]
    if any(word in message.casefold() for word in ("experiment", "accuracy", "precision", "recall", "f1", "model", "prediction")):
        return records[:5]
    return []


def _context(db: Session, companies: list[Company], events: list[Event], experiments: list[dict[str, Any]]):
    citations: list[dict[str, Any]] = []
    event_rows = []
    for event in events:
        risk = max(event.risk_assessments, key=lambda row: row.id, default=None)
        row = {
            "id": event.id,
            "company_id": event.company_id,
            "title": event.title,
            "category": event.category,
            "status": event.status,
            "occurred_at": event.occurred_at.isoformat(),
            "risk": None if not risk else {"priority": risk.priority, "overall_score": risk.overall_score, "explanation": risk.explanation},
            "evidence": [],
        }
        for evidence in event.evidence:
            observation = db.get(Observation, evidence.observation_id)
            source = db.get(Source, observation.source_id) if observation else None
            if not observation:
                continue
            citation = {
                "id": len(citations) + 1,
                "type": "observation",
                "record_id": observation.id,
                "title": observation.title,
                "url": observation.url,
                "published_at": observation.published_at.isoformat() if observation.published_at else None,
                "collected_at": observation.collected_at.isoformat(),
                "source_status": source.last_status if source else None,
                "verification_status": evidence.verification_status,
                "excerpt": evidence.excerpt,
            }
            citations.append(citation)
            row["evidence"].append({"citation_id": citation["id"], "excerpt": evidence.excerpt, "verification_status": evidence.verification_status})
        event_rows.append(row)
    return {"companies": [{"id": c.id, "name": c.name, "industry": c.industry, "description": c.description} for c in companies], "events": event_rows, "experiments": experiments}, citations


def _experiment_answer(exp: dict[str, Any]) -> str:
    metrics = exp.get("metrics", {})
    dataset = exp.get("dataset", {})
    return (
        f"Experiment {exp.get('id')} is a {exp.get('task')} experiment using "
        f"{metrics.get('model_type', 'the stored model')} on {dataset.get('row_count', dataset.get('rows', 'an unknown number'))} rows. "
        f"The held-out accuracy is {metrics.get('accuracy', 0) * 100:.1f}% and macro-F1 is "
        f"{metrics.get('macro_f1', 0) * 100:.1f}%, compared with a most-frequent baseline of "
        f"{metrics.get('baseline', {}).get('accuracy', 0) * 100:.1f}% accuracy. "
        "These metrics describe the stored event-classification experiment only; they do not validate "
        "stock movement, sentiment, anomaly detection, or business-risk prediction."
    )
