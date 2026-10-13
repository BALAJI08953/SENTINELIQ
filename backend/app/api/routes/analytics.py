from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Company, Event, Evidence, Observation, RiskAssessment, Source, UserSettings
from app.models.entities import EVENT_CATEGORIES
from app.schemas import SettingsIO

router = APIRouter(tags=["analytics"])
PRIORITIES = ["low", "medium", "high", "critical"]


def _latest_risk(db: Session) -> dict[str, int]:
    latest = select(func.max(RiskAssessment.id)).group_by(RiskAssessment.event_id)
    rows = db.execute(select(RiskAssessment.priority, func.count()).where(RiskAssessment.id.in_(latest))
                      .group_by(RiskAssessment.priority)).all()
    out = dict.fromkeys(PRIORITIES, 0)
    out.update({k: v for k, v in rows})
    return out


def _count(db: Session, model, *where) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*where)) or 0


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "database": "ok"}


@router.get("/analytics/overview")
def overview(db: Session = Depends(get_db)):
    pr = _latest_risk(db)
    return {
        "companies": _count(db, Company), "observations": _count(db, Observation),
        "events": _count(db, Event), "new_events": _count(db, Event, Event.status == "new"),
        "high_priority": pr["high"], "critical": pr["critical"],
        "claims_awaiting_verification": _count(db, Evidence, Evidence.verification_status == "unverified"),
        "sources_ok": _count(db, Source, Source.last_status == "ok"),
        "sources_error": _count(db, Source, Source.last_status == "error"),
        "sources_never_collected": _count(db, Source, Source.last_status.is_(None)),
        "demo_events": _count(db, Event, Event.is_demo.is_(True)),
        "real_events": _count(db, Event, Event.is_demo.is_(False)),
    }


@router.get("/analytics/timeline")
def timeline(db: Session = Depends(get_db)):
    day = func.date(Event.occurred_at)
    rows = db.execute(select(day, func.count()).group_by(day).order_by(day)).all()
    return [{"date": str(d), "events": n} for d, n in rows]


@router.get("/analytics/categories")
def categories(db: Session = Depends(get_db)):
    rows = dict(db.execute(select(Event.category, func.count()).group_by(Event.category)).all())
    return [{"category": c, "count": rows.get(c, 0)} for c in EVENT_CATEGORIES]


@router.get("/analytics/priorities")
def priorities(db: Session = Depends(get_db)):
    pr = _latest_risk(db)
    return [{"priority": p, "count": pr[p]} for p in PRIORITIES]


@router.get("/analytics/companies")
def company_activity(db: Session = Depends(get_db)):
    ev = dict(db.execute(select(Event.company_id, func.count()).group_by(Event.company_id)).all())
    ob = dict(db.execute(select(Observation.company_id, func.count()).group_by(Observation.company_id)).all())
    return [{"company_id": c.id, "name": c.name, "events": ev.get(c.id, 0), "observations": ob.get(c.id, 0)}
            for c in db.scalars(select(Company).order_by(Company.name)).all()]


def _settings(db: Session) -> UserSettings:
    s = db.get(UserSettings, 1)
    if not s:
        s = UserSettings(id=1)
        db.add(s)
        db.commit()
    return s


@router.get("/settings", response_model=SettingsIO)
def get_settings(db: Session = Depends(get_db)):
    s = _settings(db)
    return SettingsIO(timezone=s.timezone, display_name=s.display_name, show_demo_data=s.show_demo_data)


@router.put("/settings", response_model=SettingsIO)
def put_settings(body: SettingsIO, db: Session = Depends(get_db)):
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        ZoneInfo(body.timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown timezone: {body.timezone}") from exc
    s = _settings(db)
    s.timezone, s.display_name, s.show_demo_data = body.timezone, body.display_name, body.show_demo_data
    db.commit()
    return body
