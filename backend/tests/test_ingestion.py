from unittest.mock import MagicMock, patch

import pytest
import requests

from app.services import companies as svc
from app.services.change_detection.pages import page_change_count
from app.services.events.extraction import extract_event, extract_events
from app.services.ingestion import providers
from app.services.ingestion.normalize import content_hash, normalize_text, normalize_url
from app.services.ingestion.providers import HTMLProvider, ProviderError, RawItem, RSSProvider
from app.services.ingestion.service import collect_source
from app.services.intelligence import process_events_pipeline

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Acme launches X</title><link>https://e.invalid/1</link>
<description>&lt;p&gt;Big   launch&lt;/p&gt;</description><pubDate>Mon, 01 Sep 2026 09:00:00 GMT</pubDate></item>
<item><title>Acme hires CTO</title><link>https://e.invalid/2</link><description>New CTO</description></item>
</channel></rss>"""


class FakeProvider:
    def __init__(self, items):
        self.items = items

    def fetch(self, source):
        return self.items


@pytest.fixture()
def source(db):
    c = svc.create_company(db, "Acme")
    return svc.add_source(db, c.id, "rss", "https://e.invalid/feed")


def test_normalization_and_hash_stability():
    assert normalize_text("<p>Big \n  launch</p>") == "Big launch"
    assert content_hash("A  Title", "<b>x</b>") == content_hash("a title", "x")
    assert content_hash("a", "x") != content_hash("a", "y")
    assert normalize_url("HTTPS://Example.COM/news?a=2&b=1#fragment") == "https://example.com/news?a=2&b=1"


def test_collect_and_dedupe(db, source):
    items = [RawItem("Launch", "<p>Body</p>", "https://e.invalid/1"), RawItem("Launch ", "Body")]
    r = collect_source(db, source, FakeProvider(items))
    assert (r.status, r.fetched, r.new, r.duplicates) == ("ok", 2, 1, 1)
    r2 = collect_source(db, source, FakeProvider(items))
    assert (r2.new, r2.duplicates) == (0, 2)
    assert source.last_status == "ok" and source.last_collected_at is not None


def test_provider_failure_is_recorded(db, source):
    class Boom:
        def fetch(self, s):
            raise ProviderError("fetch failed: 503")

    r = collect_source(db, source, Boom())
    assert r.status == "error" and "503" in r.error
    assert source.last_status == "error" and "503" in source.last_error


def test_rss_provider_parses_mocked_feed(db, source):
    resp = MagicMock(content=RSS)
    resp.raise_for_status.return_value = None
    with patch.object(providers.requests, "get", return_value=resp):
        items = RSSProvider().fetch(source)
    assert [i.title for i in items] == ["Acme launches X", "Acme hires CTO"]
    assert items[0].published_at is not None and items[1].published_at is None


def test_network_error_becomes_provider_error(db, source):
    with patch.object(providers.requests, "get", side_effect=requests.ConnectionError("down")), \
            pytest.raises(ProviderError):
        RSSProvider().fetch(source)


def test_html_provider_respects_robots(db):
    c = svc.create_company(db, "Acme")
    s = svc.add_source(db, c.id, "html", "https://e.invalid/pricing")
    robots = MagicMock(status_code=200, text="User-agent: *\nDisallow: /pricing")
    with patch.object(providers.requests, "get", return_value=robots) as get, \
            pytest.raises(ProviderError, match="robots"):
        HTMLProvider().fetch(s)
    assert get.call_count == 1  # page itself was never requested


def test_html_snapshot_change_detection(db):
    c = svc.create_company(db, "Acme")
    s = svc.add_source(db, c.id, "html", "https://e.invalid/pricing")

    def run(html):
        robots = MagicMock(status_code=404, text="")
        page = MagicMock(text=html)
        page.raise_for_status.return_value = None
        with patch.object(providers.requests, "get", side_effect=[robots, page]):
            return collect_source(db, s)

    assert run("<title>P</title><body>Price $10</body>").new == 1
    assert run("<title>P</title><body>Price $10</body>").new == 0  # unchanged -> deduplicated
    assert run("<title>P</title><body>Price $8</body>").new == 1  # changed -> new snapshot
    assert page_change_count(db, s) == 1


def test_event_extraction_links_evidence_once(db, source):
    r = collect_source(db, source, FakeProvider([RawItem("Acme raises funds", "Series B", "https://e.invalid/3")]))
    ev = extract_event(db, r.new_observation_ids[0])
    assert ev.category == "other" and len(ev.evidence) == 1
    assert ev.evidence[0].observation_id == r.new_observation_ids[0]
    assert extract_event(db, r.new_observation_ids[0]) is None  # no duplicate event
    assert extract_events(db, r.new_observation_ids) == []
    with pytest.raises(ValueError):
        extract_event(db, 9999)


def test_pipeline_is_safe_to_rerun_without_duplicate_risk(db, source, monkeypatch, tmp_path):
    r = collect_source(db, source, FakeProvider([RawItem("Acme raises funds", "Series B", "https://e.invalid/3")]))
    event = extract_event(db, r.new_observation_ids[0])
    assert event is not None

    from app.ml import predict as predict_mod
    from app.ml.train import train

    model_path = tmp_path / "model.joblib"
    train(model_path=model_path, metrics_path=tmp_path / "metrics.json")
    monkeypatch.setattr(predict_mod, "MODEL_PATH", model_path)
    first = process_events_pipeline(db, [event])[0]
    second = process_events_pipeline(db, [event])[0]
    assert first.risk_status == "assessed"
    assert second.risk_status == "already_assessed"
    assert second.prediction_status == "already_classified"
    assert len(event.risk_assessments) == 1
