def test_sentrix_answers_from_persisted_records_with_citations(seeded):
    response = seeded.post(
        "/api/v1/sentrix/chat",
        json={"message": "Summarize the latest developments", "company_id": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["assistant"] == "SENTRIX"
    assert body["provider"] == "deterministic_grounded"
    assert "Northwind" in body["answer"]
    assert body["citations"]
    assert body["records"]["companies"] == [1]
    assert body["citations"][0]["verification_status"] == "unverified"


def test_sentrix_reports_insufficient_evidence(seeded):
    response = seeded.post(
        "/api/v1/sentrix/chat",
        json={"message": "Tell me about a company that does not exist"},
    )
    assert response.status_code == 200
    assert "could not find supporting" in response.json()["answer"].lower()


def test_sentrix_answers_broad_risk_question(seeded):
    response = seeded.post(
        "/api/v1/sentrix/chat",
        json={"message": "Which events have the highest risk scores, and why?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "could not find supporting" not in body["answer"].lower()
    assert "risk high (76/100)" in body["answer"]
    assert body["records"]["events"]


def test_sentrix_rejects_unknown_context_record(seeded):
    response = seeded.post(
        "/api/v1/sentrix/chat",
        json={"message": "Summarize this", "company_id": 9999},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
