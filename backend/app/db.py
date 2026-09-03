from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_settings


def _make_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=10,
        future=True,
    )


_settings = get_settings()
engine = _make_engine(_settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
