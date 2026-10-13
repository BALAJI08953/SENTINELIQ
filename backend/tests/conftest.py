import pytest
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.database import Base, make_engine


@pytest.fixture()
def db():
    eng = make_engine("sqlite://")
    Base.metadata.create_all(eng)
    with sessionmaker(bind=eng, expire_on_commit=False)() as session:
        yield session
