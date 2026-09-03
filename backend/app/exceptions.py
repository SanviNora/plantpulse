"""S&OP exception detectors ranked by dollar impact."""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import (
    BIAS_THRESHOLD,
    BIAS_WEEKS,
    COVER_WEEKS,
    CURRENT_WEEK,
    FAMILY_SCRAP,
    PLANTS,
    SCRAP_SPIKE_MULTIPLIER,
    SKUS,
)
from .generate import Snapshot


STOCKOUT = "stockout_risk"
BIAS = "forecast_bias"
OVERTIME = "capacity_overtime"
SCRAP = "scrap_spike"


@dataclass(frozen=True)
class ExceptionItem:
    code: str
    kind: str
    title: str
    dollar_impact: float
    recommendation: str
    action: str
    sku_code: str | None
    dc_code: str | None
    plant_code: str | None
    detail: str


def _sku(code: str):
    return next(s for s in SKUS if s.sku_code == code)


def _plant(code: str):
    return next(p for p in PLANTS if p.plant_code == code)


def detect_stockouts(snapshot: Snapshot, week: int = CURRENT_WEEK) -> list[ExceptionItem]:
    items: list[ExceptionItem] = []
    rows = [r for r in snapshot.demand if r.week == week]
    for row in rows:
        cover = row.on_hand + row.incoming
        need = row.forecast_units * COVER_WEEKS
        gap = need - cover
        if gap <= 0:
            continue
        sku = _sku(row.sku_code)
        dollars = round(gap * sku.stockout_penalty, 2)
        items.append(
            ExceptionItem(
                code=f"stockout-{row.sku_code}-{row.dc_code}-w{week}",
                kind=STOCKOUT,
                title=f"{row.sku_code} at {row.dc_code} covers under {COVER_WEEKS:.0f} weeks",
                dollar_impact=dollars,
                recommendation=(
                    f"Expedite {gap:.0f} units into {row.dc_code} or buy a Fort Worth "
                    f"weekend shift before the next order cycle."
                ),
                action="expedite_or_extra_shift",
                sku_code=row.sku_code,
                dc_code=row.dc_code,
                plant_code=None,
                detail=f"on_hand={row.on_hand:.0f} incoming={row.incoming:.0f} need={need:.0f}",
            )
        )
    return items


def detect_forecast_bias(snapshot: Snapshot, week: int = CURRENT_WEEK) -> list[ExceptionItem]:
    items: list[ExceptionItem] = []
    start = week - BIAS_WEEKS + 1
    keys = {(r.sku_code, r.dc_code) for r in snapshot.demand}
    for sku_code, dc_code in sorted(keys):
        window = [
            r
            for r in snapshot.demand
            if r.sku_code == sku_code and r.dc_code == dc_code and start <= r.week <= week
        ]
        if len(window) < BIAS_WEEKS:
            continue
        numer = sum(r.actual_units - r.forecast_units for r in window)
        denom = sum(r.forecast_units for r in window)
        if denom <= 0:
            continue
        bias = numer / denom
        if abs(bias) < BIAS_THRESHOLD:
            continue
        sku = _sku(sku_code)
        dollars = round(abs(bias) * sku.base_forecast * sku.stockout_penalty * 4.0, 2)
        direction = "under-forecast" if bias > 0 else "over-forecast"
        items.append(
            ExceptionItem(
                code=f"bias-{sku_code}-{dc_code}-w{week}",
                kind=BIAS,
                title=f"{sku_code} {dc_code} is {direction} by {abs(bias)*100:.1f}%",
                dollar_impact=dollars,
                recommendation=(
                    "Do not promote the one-step model. Keep the seasonal naive in "
                    "production until a recursive backtest beats it on this series."
                ),
                action="hold_registry_promotion",
                sku_code=sku_code,
                dc_code=dc_code,
                plant_code=None,
                detail=f"bias={bias:.4f} window={BIAS_WEEKS}w",
            )
        )
    return items


def detect_overtime(snapshot: Snapshot, week: int = CURRENT_WEEK) -> list[ExceptionItem]:
    items: list[ExceptionItem] = []
    for row in snapshot.capacity:
        if row.week != week:
            continue
        extra = row.hours_used - row.hours_available
        if extra <= 0:
            continue
        plant = _plant(row.plant_code)
        dollars = round(extra * plant.overtime_usd_per_hour, 2)
        items.append(
            ExceptionItem(
                code=f"ot-{row.plant_code}-w{week}",
                kind=OVERTIME,
                title=f"{plant.name} is {extra:.1f} hours over the weekly cap",
                dollar_impact=dollars,
                recommendation=(
                    f"Move {extra:.1f} hours of Daily Disposable off {plant.name} or "
                    f"approve overtime at ${plant.overtime_usd_per_hour:.0f}/hour."
                ),
                action="rebalance_or_buy_hours",
                sku_code=None,
                dc_code=None,
                plant_code=row.plant_code,
                detail=f"used={row.hours_used:.1f} available={row.hours_available:.1f}",
            )
        )
    return items


def detect_scrap_spikes(snapshot: Snapshot, week: int = CURRENT_WEEK) -> list[ExceptionItem]:
    items: list[ExceptionItem] = []
    sku_by = {s.sku_code: s for s in SKUS}
    for row in snapshot.scrap:
        if row.week != week or row.units <= 0:
            continue
        sku = sku_by[row.sku_code]
        baseline = FAMILY_SCRAP[sku.family]
        rate = row.scrap_units / row.units
        if rate < baseline * SCRAP_SPIKE_MULTIPLIER:
            continue
        dollars = round(row.scrap_units * sku.unit_cost, 2)
        items.append(
            ExceptionItem(
                code=f"scrap-{row.plant_code}-{row.sku_code}-w{week}",
                kind=SCRAP,
                title=f"{row.sku_code} scrap on {row.plant_code} is {rate*100:.1f}% vs {baseline*100:.1f}% baseline",
                dollar_impact=dollars,
                recommendation=(
                    "Hold the next Toric campaign on this line until incoming inspection "
                    "clears the last lot. Do not buy extra hours into a scrap spike."
                ),
                action="hold_run_inspect_lot",
                sku_code=row.sku_code,
                dc_code=None,
                plant_code=row.plant_code,
                detail=f"rate={rate:.4f} baseline={baseline:.4f}",
            )
        )
    return items


def rank_exceptions(snapshot: Snapshot, week: int = CURRENT_WEEK) -> list[ExceptionItem]:
    items = [
        *detect_stockouts(snapshot, week),
        *detect_forecast_bias(snapshot, week),
        *detect_overtime(snapshot, week),
        *detect_scrap_spikes(snapshot, week),
    ]
    items.sort(key=lambda e: (-e.dollar_impact, e.code))
    return items
