from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import PageParams
from app.core.database import get_db
from app.models import CompanyRelationship, Event, Observation, Source
from app.schemas import (
    CompanyIn,
    CompanyOut,
    CompanyUpdate,
    EventOut,
    Page,
    RelationshipIn,
    RelationshipOut,
    SourceIn,
    SourceOut,
)
from app.services import companies as svc
from app.services.events.extraction import extract_events
from app.services.ingestion.service import collect_source
from app.services.intelligence import process_events_pipeline

router = APIRouter(tags=["companies"])


@router.get("/companies", response_model=Page[CompanyOut])
def list_companies(q: str | None = None, p: PageParams = Depends(), db: Session = Depends(get_db)):
    items, total = svc.list_companies(db, q, p.offset, p.limit)
    return Page(items=items, total=total, offset=p.offset, limit=p.limit)


@router.post("/companies", response_model=CompanyOut, status_code=201)
def create_company(body: CompanyIn, db: Session = Depends(get_db)):
    data = body.model_dump(exclude={"name"})
    data["website"] = str(body.website) if body.website else None
    return svc.create_company(db, body.name, **data)


@router.get("/companies/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    return svc.get_company(db, company_id)


@router.patch("/companies/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, body: CompanyUpdate, db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    if data.get("website"):
        data["website"] = str(data["website"])
    return svc.update_company(db, company_id, **data)


@router.delete("/companies/{company_id}", status_code=204)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    svc.delete_company(db, company_id)
    return Response(status_code=204)


@router.get("/companies/{company_id}/events", response_model=Page[EventOut])
def company_events(company_id: int, p: PageParams = Depends(), db: Session = Depends(get_db)):
    svc.get_company(db, company_id)
    stmt = select(Event).where(Event.company_id == company_id)
    total = len(db.scalars(stmt).all())
    items = db.scalars(stmt.order_by(Event.occurred_at.desc()).offset(p.offset).limit(p.limit)).all()
    return Page(items=items, total=total, offset=p.offset, limit=p.limit)


@router.get("/companies/{company_id}/timeline")
def company_timeline(company_id: int, db: Session = Depends(get_db)):
    svc.get_company(db, company_id)
    evs = db.scalars(select(Event).where(Event.company_id == company_id).order_by(Event.occurred_at)).all()
    return [{"event_id": e.id, "date": e.occurred_at.date().isoformat(), "title": e.title,
             "category": e.category, "is_demo": e.is_demo} for e in evs]


@router.get("/companies/{company_id}/sources", response_model=list[SourceOut])
def company_sources(company_id: int, db: Session = Depends(get_db)):
    svc.get_company(db, company_id)
    return svc.list_sources(db, company_id)


@router.get("/sources", response_model=Page[SourceOut])
def list_sources(p: PageParams = Depends(), db: Session = Depends(get_db)):
    stmt = select(Source).order_by(Source.last_collected_at.desc().nullslast(), Source.id.desc())
    total = len(db.scalars(select(Source)).all())
    return Page(items=db.scalars(stmt.offset(p.offset).limit(p.limit)).all(), total=total, offset=p.offset, limit=p.limit)


@router.post("/companies/{company_id}/sources", response_model=SourceOut, status_code=201)
def add_source(company_id: int, body: SourceIn, db: Session = Depends(get_db)):
    return svc.add_source(db, company_id, body.kind, body.url, body.label, is_demo=body.kind == "demo")


@router.delete("/sources/{source_id}", status_code=204)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    svc.delete_source(db, source_id)
    return Response(status_code=204)


@router.post("/sources/{source_id}/collect")
def collect(source_id: int, extract: bool = True, db: Session = Depends(get_db)):
    from app.models import Source
    src = db.get(Source, source_id)
    if not src:
        raise svc.NotFoundError(f"Source {source_id} not found")
    res = collect_source(db, src)
    events = extract_events(db, res.new_observation_ids) if extract else []
    processing = process_events_pipeline(db, events)
    return {"status": res.status, "fetched": res.fetched, "new": res.new, "duplicates": res.duplicates,
            "error": res.error, "events_created": len(events),
            "events_processed": len(processing),
            "model_unavailable": sum(x.prediction_status == "model_unavailable" for x in processing),
            "risk_assessments_created": sum(x.risk_status == "assessed" for x in processing)}


@router.get("/companies/{company_id}/relationships", response_model=list[RelationshipOut])
def list_relationships(company_id: int, db: Session = Depends(get_db)):
    svc.get_company(db, company_id)
    return db.scalars(select(CompanyRelationship).where(CompanyRelationship.company_id == company_id)).all()


@router.post("/companies/{company_id}/relationships", response_model=RelationshipOut, status_code=201)
def add_relationship(company_id: int, body: RelationshipIn, db: Session = Depends(get_db)):
    svc.get_company(db, company_id)
    svc.get_company(db, body.related_company_id)
    if body.verification_status == "verified":
        obs = db.get(Observation, body.evidence_observation_id) if body.evidence_observation_id else None
        if obs is None:
            raise ValueError("A 'verified' relationship requires a valid evidence_observation_id")
    row = CompanyRelationship(company_id=company_id, **body.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise svc.ConflictError("Invalid or duplicate relationship") from exc
    return row
