from app.ml import predict as predict_mod
from app.ml.train import train

P = "/api/v1"


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


def test_reports_are_generated_from_persisted_data_and_exported(seeded):
    created = seeded.post(f"{P}/reports", json={"company_id": 1})
    assert created.status_code == 201
    report = created.json()
    assert report["company_id"] == 1
    assert report["content_json"]["events"]
    assert "Important events" in report["content_markdown"]

    listed = seeded.get(f"{P}/reports?company_id=1").json()
    assert listed["total"] >= 1
    report_id = report["id"]
    markdown = seeded.get(f"{P}/reports/{report_id}/export?format=markdown")
    assert markdown.status_code == 200
    assert markdown.headers["content-type"].startswith("text/markdown")
    assert b"Northwind Analytics" in markdown.content
    exported_json = seeded.get(f"{P}/reports/{report_id}/export?format=json")
    assert exported_json.status_code == 200
    assert exported_json.json()["company"]["name"] == "Northwind Analytics"
    assert seeded.get(f"{P}/reports/{report_id}/export?format=csv").status_code == 422


def test_deterministic_insights_and_decision_support(seeded):
    eid = seeded.get(f"{P}/events").json()["items"][0]["id"]
    insight = seeded.get(f"{P}/events/{eid}/insights")
    assert insight.status_code == 200
    body = insight.json()
    assert body["provider"] == "deterministic_local"
    assert body["source_facts"]
    assert "uncertainties" in body

    options = seeded.get(f"{P}/events/{eid}/decision-support")
    assert options.status_code == 200
    assert len(options.json()["options"]) == 3
    assert "not automatic recommendations" in options.json()["disclaimer"]


def test_workflows_schedules_mock_delivery_and_logs(seeded):
    created = seeded.post(f"{P}/workflows", json={
        "name": "Demo daily review",
        "company_ids": [1],
        "categories": ["pricing_change"],
        "min_priority": "medium",
        "report_type": "daily",
    })
    assert created.status_code == 201
    wid = created.json()["id"]
    assert seeded.patch(f"{P}/workflows/{wid}", json={"enabled": False}).json()["enabled"] is False

    bad_schedule = seeded.post(f"{P}/workflows/{wid}/schedules", json={"mode": "interval", "timezone": "UTC"})
    assert bad_schedule.status_code == 422
    schedule = seeded.post(f"{P}/workflows/{wid}/schedules", json={
        "mode": "daily", "time_of_day": "08:30", "timezone": "Asia/Kolkata",
    })
    assert schedule.status_code == 201
    sid = schedule.json()["id"]

    recipient = seeded.post(f"{P}/schedules/{sid}/recipients", json={
        "channel": "email", "address": "demo@example.invalid", "authorized": True,
    })
    assert recipient.status_code == 201
    provider = seeded.get(f"{P}/notification-providers").json()["providers"][0]
    assert provider["name"] == "mock" and provider["status"] == "available"

    run = seeded.post(f"{P}/workflows/{wid}/execute")
    assert run.status_code == 200
    assert run.json()["reports_created"] == 1
    assert run.json()["simulated"] == 1
    logs = seeded.get(f"{P}/delivery-logs").json()
    assert logs["total"] >= 1
    assert logs["items"][0]["provider"] == "mock"
