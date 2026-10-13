import pytest

from app.models import Company
from app.services import companies as svc


def test_company_crud_roundtrip(db):
    c = svc.create_company(db, "  Acme  ", industry="Tools")
    assert c.name == "Acme"
    assert svc.get_company(db, c.id).industry == "Tools"
    svc.update_company(db, c.id, description="desc", industry=None)
    assert svc.get_company(db, c.id).description == "desc"
    assert svc.get_company(db, c.id).industry == "Tools"  # None means "leave unchanged"
    svc.delete_company(db, c.id)
    with pytest.raises(svc.NotFoundError):
        svc.get_company(db, c.id)


def test_duplicate_and_blank_names(db):
    svc.create_company(db, "Acme")
    with pytest.raises(svc.ConflictError):
        svc.create_company(db, "Acme")
    with pytest.raises(ValueError):
        svc.create_company(db, "   ")
    assert db.query(Company).count() == 1  # failed insert was rolled back


def test_search_and_pagination(db):
    for n in ("Alpha Co", "Beta Co", "Alphabet Inc"):
        svc.create_company(db, n)
    items, total = svc.list_companies(db, q="alpha")
    assert total == 2 and {c.name for c in items} == {"Alpha Co", "Alphabet Inc"}
    items, total = svc.list_companies(db, limit=1, offset=1)
    assert total == 3 and len(items) == 1


def test_source_validation_and_cascade(db):
    c = svc.create_company(db, "Acme")
    with pytest.raises(ValueError):
        svc.add_source(db, c.id, "rss", "ftp://bad")
    with pytest.raises(ValueError):
        svc.add_source(db, c.id, "twitter", "https://x")
    s = svc.add_source(db, c.id, "rss", "https://example.invalid/feed")
    with pytest.raises(svc.ConflictError):
        svc.add_source(db, c.id, "rss", "https://example.invalid/feed")
    with pytest.raises(svc.NotFoundError):
        svc.add_source(db, 999, "rss", "https://example.invalid/x")
    assert [x.id for x in svc.list_sources(db, c.id)] == [s.id]
    svc.delete_company(db, c.id)
    assert svc.list_sources(db) == []
