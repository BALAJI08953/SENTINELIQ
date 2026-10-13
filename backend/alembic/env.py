from sqlalchemy import create_engine

import app.models  # noqa: F401
from alembic import context
from app.core.config import settings
from app.core.database import Base

target_metadata = Base.metadata


def run_migrations_online() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
