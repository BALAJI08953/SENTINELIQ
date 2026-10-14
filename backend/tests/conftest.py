import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
import scripts.seed as seed_mod
from app.core.database import Base, get_db, make_engine
from app.main import create_app


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


@pytest.fixture()
def db():
    eng = make_engine("sqlite://")
    Base.metadata.create_all(eng)
    with sessionmaker(bind=eng, expire_on_commit=False)() as session:
        yield session
