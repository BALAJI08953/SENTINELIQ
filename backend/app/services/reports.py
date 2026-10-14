from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Company, Event, Observation, Report
from app.services.companies import NotFoundError


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _period_filter(stmt, start: datetime | None, end: datetime | None):
    if start:
        stmt = stmt.where(Event.occurred_at >= start)
    if end:
        stmt = stmt.where(Event.occurred_at <= end)
    return stmt


def build_company_report(
    db: Session,
    company_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
) -> tuple[str, dict, str]:
    company = db.get(Company, company_id)
    if not company:
        raise NotFoundError(f"Company {company_id} not found")

    event_stmt = select(Event).where(Event.company_id == company_id)
    event_stmt = _period_filter(event_stmt, start, end)
    events = db.scalars(
        event_stmt.options(
            selectinload(Event.evidence),
            selectinload(Event.predictions),
            selectinload(Event.risk_assessments),
        ).order_by(Event.occurred_at.desc(), Event.id.desc())
    ).all()

    obs_stmt = select(Observation).where(Observation.company_id == company_id)
    if start:
        obs_stmt = obs_stmt.where(Observation.collected_at >= start)
    if end:
        obs_stmt = obs_stmt.where(Observation.collected_at <= end)
    observations = db.scalars(obs_stmt.order_by(Observation.collected_at.desc()).limit(20)).all()

    generated_at = datetime.now(UTC)
    title = f"{company.name} intelligence report"
    content = {
        "company": {"id": company.id, "name": company.name, "industry": company.industry},
        "period": {"start": _iso(start), "end": _iso(end)},
        "generated_at": generated_at.isoformat(),
        "limitations": [
            "Report is generated only from persisted SentinelIQ data.",
            "Model outputs are decision-support signals, not confirmed facts.",
        ],
        "events": [],
        "recent_observations": [
            {
                "id": o.id,
                "title": o.title,
                "url": o.url,
                "published_at": _iso(o.published_at),
                "collected_at": _iso(o.collected_at),
            }
            for o in observations
        ],
    }

    for event in events:
        latest_risk = max(event.risk_assessments, key=lambda r: r.id, default=None)
        latest_prediction = max(event.predictions, key=lambda p: p.id, default=None)
        content["events"].append(
            {
                "id": event.id,
                "title": event.title,
                "category": event.category,
                "status": event.status,
                "occurred_at": _iso(event.occurred_at),
                "prediction": None
                if latest_prediction is None
                else {
                    "label": latest_prediction.label,
                    "confidence": latest_prediction.confidence,
                    "model_version": latest_prediction.model_version,
                },
                "risk_assessment": None
                if latest_risk is None
                else {
                    "overall_score": latest_risk.overall_score,
                    "priority": latest_risk.priority,
                    "explanation": latest_risk.explanation,
                    "factors": {
                        "impact": latest_risk.impact,
                        "urgency": latest_risk.urgency,
                        "strategic_relevance": latest_risk.strategic_relevance,
                        "evidence_quality": latest_risk.evidence_quality,
                    },
                },
                "evidence": [
                    {
                        "observation_id": ev.observation_id,
                        "excerpt": ev.excerpt,
                        "verification_status": ev.verification_status,
                    }
                    for ev in event.evidence
                ],
            }
        )

    md = render_markdown(title, content)
    return title, content, md


def render_markdown(title: str, content: dict) -> str:
    lines = [
        f"# {title}",
        "",
        f"Generated: {content['generated_at']}",
        f"Company: {content['company']['name']}",
        f"Period: {content['period']['start'] or 'all time'} to {content['period']['end'] or 'now'}",
        "",
        "## Important events",
    ]
    if not content["events"]:
        lines.append("No events were found for this reporting period.")
    for event in content["events"]:
        lines.extend(["", f"### {event['title']}", f"- Category: {event['category']}"])
        risk = event["risk_assessment"]
        if risk:
            lines.append(f"- Risk: {risk['overall_score']} ({risk['priority']})")
            lines.append(f"- Explanation: {risk['explanation']}")
        pred = event["prediction"]
        if pred:
            lines.append(
                f"- Model signal: {pred['label']} at {pred['confidence']:.2f} confidence "
                f"({pred['model_version']})"
            )
        if event["evidence"]:
            lines.append("- Supporting evidence:")
            for ev in event["evidence"]:
                lines.append(
                    f"  - Observation {ev['observation_id']} ({ev['verification_status']}): "
                    f"{ev['excerpt'] or 'No excerpt'}"
                )
    lines.extend(["", "## Recent observations"])
    if not content["recent_observations"]:
        lines.append("No observations were found for this reporting period.")
    for obs in content["recent_observations"]:
        suffix = f" - {obs['url']}" if obs["url"] else ""
        lines.append(f"- {obs['title']}{suffix}")
    lines.extend(["", "## Limitations", *[f"- {x}" for x in content["limitations"]]])
    return "\n".join(lines) + "\n"


def create_company_report(
    db: Session,
    company_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
) -> Report:
    company = db.get(Company, company_id)
    if not company:
        raise NotFoundError(f"Company {company_id} not found")
    title, content, markdown = build_company_report(db, company_id, start, end)
    row = Report(
        report_type="company",
        title=title,
        company_id=company_id,
        content_json=content,
        content_markdown=markdown,
        is_demo=company.is_demo,
    )
    db.add(row)
    db.commit()
    return row
