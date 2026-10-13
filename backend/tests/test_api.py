import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
import scripts.seed as seed_mod
from app.core.database import Base, get_db
from app.main import create_app
from app.ml import predict as predict_mod
from app.ml.train import train

P = "/api/v1"


@pytest.fixture()
def client():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng)
    Session = sessionmaker(bind=eng, expire_on_commit=False)
    app = create_app()

    def override():
        with Session() as s:
            yield s

    app.dependency_overrides[get_db] = override
    app.state.Session, app.state.engine = Session, eng
    return TestClient(app)


@pytest.fixture()
def seeded(client, monkeypatch):
    monkeypatch.setattr(seed_mod, "SessionLocal", client.app.state.Session)
    monkeypatch.setattr(seed_mod, "engine", client.app.state.engine)
    seed_mod.seed()
    return client


def test_health(client):
    assert client.get(f"{P}/health").json() == {"status": "ok", "database": "ok"}


def test_company_crud_and_errors(client):
    r = client.post(f"{P}/companies", json={"name": "Acme", "website": "https://acme.example.com"})
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.post(f"{P}/companies", json={"name": "Acme"}).status_code == 409
    assert client.post(f"{P}/companies", json={"name": ""}).status_code == 422
    assert client.post(f"{P}/companies", json={"name": "X", "website": "not a url"}).status_code == 422
    assert client.patch(f"{P}/companies/{cid}", json={"industry": "Tools"}).json()["industry"] == "Tools"
    assert client.get(f"{P}/companies?q=acm").json()["total"] == 1
    assert client.delete(f"{P}/companies/{cid}").status_code == 204
    r = client.get(f"{P}/companies/{cid}")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"


def test_pagination_validation(client):
    assert client.get(f"{P}/companies?limit=0").status_code == 422
    assert client.get(f"{P}/companies?offset=-1").status_code == 422


def test_sources_and_collect_demo_source(client):
    cid = client.post(f"{P}/companies", json={"name": "Acme"}).json()["id"]
    assert client.post(f"{P}/companies/{cid}/sources", json={"kind": "rss", "url": "ftp://x"}).status_code == 422
    s = client.post(f"{P}/companies/{cid}/sources", json={"kind": "demo", "url": "demo://acme"})
    assert s.status_code == 201 and s.json()["is_demo"] is True
    r = client.post(f"{P}/sources/{s.json()['id']}/collect").json()
    assert r["status"] == "ok" and r["new"] == 0
    assert client.post(f"{P}/sources/999/collect").status_code == 404


def test_seeded_analytics_come_from_database(seeded):
    o = seeded.get(f"{P}/analytics/overview").json()
    assert (o["companies"], o["observations"], o["events"]) == (5, 20, 15)
    assert o["demo_events"] == 15 and o["real_events"] == 0
    pri = {x["priority"]: x["count"] for x in seeded.get(f"{P}/analytics/priorities").json()}
    assert sum(pri.values()) == 15 and o["high_priority"] == pri["high"] and o["critical"] == pri["critical"]
    cats = {x["category"]: x["count"] for x in seeded.get(f"{P}/analytics/categories").json()}
    assert sum(cats.values()) == 15 and len(cats) == 9
    assert sum(t["events"] for t in seeded.get(f"{P}/analytics/timeline").json()) == 15
    assert len(seeded.get(f"{P}/analytics/companies").json()) == 5


def test_events_filters_detail_update_feedback(seeded):
    ev = seeded.get(f"{P}/events?category=pricing_change").json()
    assert ev["total"] == 2
    eid = ev["items"][0]["id"]
    d = seeded.get(f"{P}/events/{eid}").json()
    assert d["evidence"] and d["risk_assessments"]
    assert seeded.patch(f"{P}/events/{eid}", json={"status": "reviewed"}).json()["status"] == "reviewed"
    assert seeded.patch(f"{P}/events/{eid}", json={"status": "bogus"}).status_code == 422
    assert seeded.post(f"{P}/events/{eid}/feedback", json={"useful": True, "correct_category": "other"}).status_code == 201
    assert seeded.get(f"{P}/events/9999").status_code == 404


def test_risk_endpoint_validates_and_scores(seeded):
    eid = seeded.get(f"{P}/events").json()["items"][0]["id"]
    assert seeded.post(f"{P}/events/{eid}/risk", json={"impact": 11, "urgency": 1, "strategic_relevance": 1}).status_code == 422
    r = seeded.post(f"{P}/events/{eid}/risk", json={"impact": 10, "urgency": 10, "strategic_relevance": 10, "evidence_quality": 10})
    assert r.status_code == 201 and r.json()["overall_score"] == 100 and r.json()["priority"] == "critical"
    assert seeded.get(f"{P}/risk-assessments?priority=critical&event_id={eid}").json()["total"] >= 1


def test_process_event_503_without_model_then_works(seeded, monkeypatch, tmp_path):
    eid = seeded.get(f"{P}/events").json()["items"][0]["id"]
    monkeypatch.setattr(predict_mod, "MODEL_PATH", tmp_path / "missing.joblib")
    r = seeded.post(f"{P}/events/{eid}/process")
    assert r.status_code == 503 and r.json()["error"]["code"] == "model_unavailable"
    train(model_path=tmp_path / "m.joblib", metrics_path=tmp_path / "m.json")
    monkeypatch.setattr(predict_mod, "MODEL_PATH", tmp_path / "m.joblib")
    ok = seeded.post(f"{P}/events/{eid}/process")
    assert ok.status_code == 200 and ok.json()["evidence"]["verified"] == 1


def test_relationships_require_evidence_for_verified(seeded):
    assert seeded.post(f"{P}/companies/1/relationships", json={"related_company_id": 2, "relationship_type": "partner",
                       "verification_status": "verified"}).status_code == 422
    assert seeded.post(f"{P}/companies/1/relationships", json={"related_company_id": 1, "relationship_type": "partner"}).status_code == 409
    ok = seeded.post(f"{P}/companies/3/relationships", json={"related_company_id": 4, "relationship_type": "supplier"})
    assert ok.status_code == 201 and ok.json()["verification_status"] == "unverified"


def test_observations_search_and_settings(seeded):
    assert seeded.get(f"{P}/observations?q=pricing&limit=5").json()["total"] >= 0
    assert seeded.get(f"{P}/observations?is_demo=false").json()["total"] == 0
    assert seeded.put(f"{P}/settings", json={"timezone": "Nowhere/Land"}).status_code == 422
    assert seeded.put(f"{P}/settings", json={"timezone": "Asia/Kolkata"}).status_code == 200
    assert seeded.get(f"{P}/settings").json()["timezone"] == "Asia/Kolkata"
