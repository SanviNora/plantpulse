from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, require_role, verify_password
from .catalog import CURRENT_WEEK
from .db import get_db
from .exceptions import rank_exceptions
from .generate import Snapshot
from .models import CapacityFact, DemandFact, ExceptionAck, ScrapFact, User
from .schemas import AckIn, ExceptionOut, MeOut, QueueOut, TokenOut

router = APIRouter()


def _snapshot(db: Session) -> Snapshot:
    from .generate import CapacityRow, DemandRow, ScrapRow

    demand = tuple(
        DemandRow(
            week=r.week,
            sku_code=r.sku_code,
            dc_code=r.dc_code,
            forecast_units=r.forecast_units,
            actual_units=r.actual_units,
            on_hand=r.on_hand,
            incoming=r.incoming,
        )
        for r in db.scalars(select(DemandFact).order_by(DemandFact.id)).all()
    )
    capacity = tuple(
        CapacityRow(
            week=r.week,
            plant_code=r.plant_code,
            hours_available=r.hours_available,
            hours_used=r.hours_used,
        )
        for r in db.scalars(select(CapacityFact).order_by(CapacityFact.id)).all()
    )
    scrap = tuple(
        ScrapRow(
            week=r.week,
            plant_code=r.plant_code,
            sku_code=r.sku_code,
            units=r.units,
            scrap_units=r.scrap_units,
        )
        for r in db.scalars(select(ScrapFact).order_by(ScrapFact.id)).all()
    )
    return Snapshot(demand, capacity, scrap)


@router.post("/auth/token", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.email == form.username))
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="incorrect email or password")
    return TokenOut(access_token=create_access_token(user.email, user.role))


@router.get("/auth/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)) -> MeOut:
    return MeOut(email=user.email, full_name=user.full_name, role=user.role)


@router.get("/exceptions", response_model=QueueOut)
def list_exceptions(
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("planner", "admin")),
) -> QueueOut:
    items = rank_exceptions(_snapshot(db), CURRENT_WEEK)
    acked = {row.code for row in db.scalars(select(ExceptionAck)).all()}
    out = [
        ExceptionOut(
            code=e.code,
            kind=e.kind,
            title=e.title,
            dollar_impact=e.dollar_impact,
            recommendation=e.recommendation,
            action=e.action,
            sku_code=e.sku_code,
            dc_code=e.dc_code,
            plant_code=e.plant_code,
            detail=e.detail,
            acknowledged=e.code in acked,
        )
        for e in items
    ]
    return QueueOut(
        week=CURRENT_WEEK,
        n=len(out),
        total_impact=round(sum(e.dollar_impact for e in items), 2),
        exceptions=out,
    )


@router.post("/exceptions/ack", response_model=ExceptionOut)
def ack_exception(
    payload: AckIn,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("planner", "admin")),
) -> ExceptionOut:
    items = {e.code: e for e in rank_exceptions(_snapshot(db), CURRENT_WEEK)}
    if payload.code not in items:
        raise HTTPException(status_code=404, detail="unknown exception")
    existing = db.scalar(select(ExceptionAck).where(ExceptionAck.code == payload.code))
    if existing is None:
        db.add(ExceptionAck(code=payload.code, acknowledged=True))
        db.commit()
    e = items[payload.code]
    return ExceptionOut(
        code=e.code,
        kind=e.kind,
        title=e.title,
        dollar_impact=e.dollar_impact,
        recommendation=e.recommendation,
        action=e.action,
        sku_code=e.sku_code,
        dc_code=e.dc_code,
        plant_code=e.plant_code,
        detail=e.detail,
        acknowledged=True,
    )
