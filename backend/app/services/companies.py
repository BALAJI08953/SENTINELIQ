"""Company and source management (service layer used by API routes in stage 4)."""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Company, Source
from app.services.ingestion.normalize import normalize_url


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def _commit(db: Session, msg: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(msg) from exc


def create_company(db: Session, name: str, **fields) -> Company:
    name = name.strip()
    if not name:
        raise ValueError("name is required")
    c = Company(name=name, **fields)
    db.add(c)
    _commit(db, f"Company '{name}' already exists")
    return c


def get_company(db: Session, company_id: int) -> Company:
    c = db.get(Company, company_id)
    if not c:
        raise NotFoundError(f"Company {company_id} not found")
    return c


def list_companies(db: Session, q: str | None = None, offset: int = 0, limit: int = 50):
    stmt = select(Company)
    if q:
        stmt = stmt.where(Company.name.ilike(f"%{q}%"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(stmt.order_by(Company.name).offset(offset).limit(limit)).all()
    return items, total


def update_company(db: Session, company_id: int, **fields) -> Company:
    c = get_company(db, company_id)
    for k, v in fields.items():
        if k in {"name", "website", "industry", "description"} and v is not None:
            setattr(c, k, v.strip() if isinstance(v, str) else v)
    _commit(db, "Company name already exists")
    return c


def delete_company(db: Session, company_id: int) -> None:
    db.delete(get_company(db, company_id))
    db.commit()


def add_source(db: Session, company_id: int, kind: str, url: str, label: str | None = None,
               is_demo: bool = False) -> Source:
    get_company(db, company_id)
    if kind not in {"rss", "html", "demo"}:
        raise ValueError("kind must be rss, html or demo")
    if kind != "demo" and not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")
    normalized_url = normalize_url(url) or url.strip()
    s = Source(company_id=company_id, kind=kind, url=normalized_url, label=label, is_demo=is_demo)
    db.add(s)
    _commit(db, "Source URL already registered for this company")
    return s


def list_sources(db: Session, company_id: int | None = None):
    stmt = select(Source)
    if company_id:
        stmt = stmt.where(Source.company_id == company_id)
    return db.scalars(stmt.order_by(Source.id)).all()


def delete_source(db: Session, source_id: int) -> None:
    s = db.get(Source, source_id)
    if not s:
        raise NotFoundError(f"Source {source_id} not found")
    db.delete(s)
    db.commit()
