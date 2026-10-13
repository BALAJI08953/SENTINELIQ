import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models import Company, Event, Evidence, Observation, RiskAssessment, Source


def test_unique_company_name(db):
    db.add(Company(name="A"))
    db.commit()
    db.add(Company(name="A"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_duplicate_observation_hash_rejected(db):
    c = Company(name="A")
    db.add(c)
    db.flush()
    s = Source(company_id=c.id, kind="demo", url="u")
    db.add(s)
    db.flush()
    db.add(Observation(source_id=s.id, company_id=c.id, title="t", content_hash="x"))
    db.commit()
    db.add(Observation(source_id=s.id, company_id=c.id, title="t2", content_hash="x"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_risk_component_check_constraint(db):
    c = Company(name="A")
    db.add(c)
    db.flush()
    e = Event(company_id=c.id, title="e")
    db.add(e)
    db.flush()
    db.add(RiskAssessment(event_id=e.id, impact=11, urgency=1, strategic_relevance=1,
                          evidence_quality=1, overall_score=1, priority="low"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_seed_counts_and_evidence(db, monkeypatch):
    import scripts.seed as seed_mod

    monkeypatch.setattr(seed_mod, "SessionLocal", lambda: db.__class__(bind=db.get_bind()))
    monkeypatch.setattr(seed_mod, "engine", db.get_bind())
    seed_mod.seed()
    counts = {m.__name__: db.scalar(select(func.count()).select_from(m)) for m in (Company, Source, Observation, Event, Evidence)}
    assert counts == {"Company": 5, "Source": 10, "Observation": 20, "Event": 15, "Evidence": 15}
    assert db.scalar(select(func.count()).select_from(Event).where(Event.is_demo.is_(False))) == 0
