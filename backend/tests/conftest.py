import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

import app.db as db_module
from app.auth import hash_password
from app.db import engine, get_db
from app.generate import generate_snapshot
from app.main import app
from app.models import Base, CapacityFact, DemandFact, ScrapFact, User

db_module.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _seed(session) -> None:
    session.add(
        User(
            email="planner@plantpulse.example.com",
            hashed_password=hash_password("planner-password"),
            full_name="Priya Nair",
            role="planner",
        )
    )
    snap = generate_snapshot()
    session.add_all(
        [
            DemandFact(
                week=r.week,
                sku_code=r.sku_code,
                dc_code=r.dc_code,
                forecast_units=r.forecast_units,
                actual_units=r.actual_units,
                on_hand=r.on_hand,
                incoming=r.incoming,
            )
            for r in snap.demand
        ]
    )
    session.add_all(
        [
            CapacityFact(
                week=r.week,
                plant_code=r.plant_code,
                hours_available=r.hours_available,
                hours_used=r.hours_used,
            )
            for r in snap.capacity
        ]
    )
    session.add_all(
        [
            ScrapFact(
                week=r.week,
                plant_code=r.plant_code,
                sku_code=r.sku_code,
                units=r.units,
                scrap_units=r.scrap_units,
            )
            for r in snap.scrap
        ]
    )
    session.commit()


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = db_module.SessionLocal()
    _seed(session)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
