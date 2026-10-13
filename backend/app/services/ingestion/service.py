from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Observation, Source
from app.services.ingestion.normalize import content_hash, normalize_text
from app.services.ingestion.providers import ProviderError, SourceProvider, provider_for


@dataclass
class CollectResult:
    source_id: int
    status: str
    fetched: int = 0
    new: int = 0
    duplicates: int = 0
    error: str | None = None
    new_observation_ids: tuple[int, ...] = ()


def collect_source(db: Session, source: Source, provider: SourceProvider | None = None) -> CollectResult:
    """Fetch, normalize and store observations; duplicates (same company + content hash) are skipped.

    Failures are recorded on the source (last_status/last_error), never silently swallowed.
    """
    now = datetime.now(UTC)
    try:
        items = (provider or provider_for(source)).fetch(source)
    except ProviderError as exc:
        source.last_status, source.last_error, source.last_collected_at = "error", str(exc), now
        db.commit()
        return CollectResult(source.id, "error", error=str(exc))

    res = CollectResult(source.id, "ok", fetched=len(items))
    new_ids = []
    for it in items:
        title, body = normalize_text(it.title, 500), normalize_text(it.body)
        digest = content_hash(title, body)
        exists = db.scalar(select(Observation.id).where(
            Observation.company_id == source.company_id, Observation.content_hash == digest))
        if exists:
            res.duplicates += 1
            continue
        obs = Observation(source_id=source.id, company_id=source.company_id, title=title, body=body,
                          url=it.url, content_hash=digest, published_at=it.published_at,
                          collected_at=now, is_demo=source.is_demo)
        db.add(obs)
        db.flush()
        new_ids.append(obs.id)
        res.new += 1
    source.last_status, source.last_error, source.last_collected_at = "ok", None, now
    db.commit()
    res.new_observation_ids = tuple(new_ids)
    return res
