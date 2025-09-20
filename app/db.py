from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .settings import get_settings

_settings = get_settings()
_engine = create_engine(_settings.database_url, echo=False, connect_args={"check_same_thread": False} if "sqlite" in _settings.database_url else {})


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)


def get_session() -> Iterator[Session]:
    # Prevent attribute expiration on commit so returned ORM instances
    # can be safely accessed outside the session scope (e.g., during
    # response assembly). This avoids DetachedInstanceError.
    with Session(_engine, expire_on_commit=False) as session:
        yield session


@contextmanager
def session_scope() -> Iterator[Session]:
    # Keep attributes available after commit to avoid triggering lazy
    # refresh on detached instances (which would require an active session).
    session = Session(_engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["init_db", "get_session", "session_scope", "_engine"]
