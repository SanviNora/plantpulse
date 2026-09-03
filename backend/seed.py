from sqlalchemy.orm import Session

from app.auth import hash_password
from app.db import SessionLocal, engine
from app.generate import generate_snapshot
from app.models import Base, CapacityFact, DemandFact, ScrapFact, User


def seed(session: Session) -> None:
    Base.metadata.create_all(engine)
    if session.query(User).first() is not None:
        return
    session.add(
        User(
            email="planner@plantpulse.example.com",
            hashed_password=hash_password("planner-password"),
            full_name="Priya Nair",
            role="planner",
        )
    )
    session.add(
        User(
            email="admin@plantpulse.example.com",
            hashed_password=hash_password("admin-password"),
            full_name="Admin",
            role="admin",
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


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
