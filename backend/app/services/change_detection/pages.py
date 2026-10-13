"""HTML pages are stored as snapshots; an unchanged page hashes identically and is deduplicated,
so each additional observation for the same source means the page content changed."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Observation, Source


def page_change_count(db: Session, source: Source) -> int:
    n = db.scalar(select(func.count()).select_from(Observation).where(Observation.source_id == source.id))
    return max((n or 0) - 1, 0)
