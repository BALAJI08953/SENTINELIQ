import pytest

from app.models import Company, Event, Evidence, Observation, Source
from app.services.evidence.verify import check_reference, verify_event_evidence
from app.services.risk.assess import assess_event, derive_evidence_quality


@pytest.fixture()
def ev(db):
    c = Company(name="A")
    db.add(c)
    db.flush()
    s = Source(company_id=c.id, kind="demo", url="u")
    db.add(s)
    db.flush()
    o = Observation(source_id=s.id, company_id=c.id, title="t", body="Acme cut prices by 10 percent",
                    url="https://e.invalid/1", content_hash="h1")
    db.add(o)
    db.flush()
    e = Event(company_id=c.id, title="Price cut")
    db.add(e)
    db.flush()
    return e, o, c


def test_reference_checks(db, ev):
    e, o, _ = ev
    assert check_reference(db, e, o.id, "https://e.invalid/1")
    assert not check_reference(db, e, o.id, "https://other.invalid")
    assert not check_reference(db, e, 9999)
    other = Company(name="B")
    db.add(other)
    db.flush()
    e2 = Event(company_id=other.id, title="x")
    db.add(e2)
    db.flush()
    assert not check_reference(db, e2, o.id)  # observation belongs to another company


def test_verify_requires_excerpt_present_in_observation(db, ev):
    e, o, _ = ev
    good = Evidence(event_id=e.id, observation_id=o.id, excerpt="cut prices by 10 percent")
    db.add(good)
    db.commit()
    db.refresh(e)
    assert verify_event_evidence(db, e) == {"verified": 1, "unverified": 0}
    good.excerpt = "fabricated claim not in source"
    db.commit()
    assert verify_event_evidence(db, e) == {"verified": 0, "unverified": 1}
    assert good.verification_status == "unverified"


def test_evidence_quality_and_assessment(db, ev):
    e, o, _ = ev
    assert derive_evidence_quality(e) == 0
    db.add(Evidence(event_id=e.id, observation_id=o.id, excerpt="cut prices", verification_status="verified"))
    db.commit()
    db.refresh(e)
    assert derive_evidence_quality(e) == 7
    row = assess_event(db, e, impact=8, urgency=8, strategic_relevance=8)
    assert row.evidence_quality == 7 and row.priority == "high" and "Heuristic" in row.explanation
    with pytest.raises(ValueError):
        assess_event(db, e, impact=11, urgency=1, strategic_relevance=1)
