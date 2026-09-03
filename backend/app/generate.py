"""Seeded weekly S&OP snapshot for a two-plant lens network."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .catalog import (
    CURRENT_WEEK,
    DCS,
    FAMILY_SCRAP,
    FTW_OVERTIME_WEEK,
    PLANTS,
    SGP_TORIC_SCRAP_WEEK,
    SKUS,
    TORIC_LIFT,
    TORIC_LIFT_FROM_WEEK,
    WEEKS,
)


@dataclass(frozen=True)
class DemandRow:
    week: int
    sku_code: str
    dc_code: str
    forecast_units: float
    actual_units: float
    on_hand: float
    incoming: float


@dataclass(frozen=True)
class CapacityRow:
    week: int
    plant_code: str
    hours_available: float
    hours_used: float


@dataclass(frozen=True)
class ScrapRow:
    week: int
    plant_code: str
    sku_code: str
    units: float
    scrap_units: float


@dataclass(frozen=True)
class Snapshot:
    demand: tuple[DemandRow, ...]
    capacity: tuple[CapacityRow, ...]
    scrap: tuple[ScrapRow, ...]


def _season(week: int) -> float:
    return 1.0 + 0.05 * math.sin(2.0 * math.pi * week / 52.0)


def generate_snapshot(seed: int = 42) -> Snapshot:
    rng = random.Random(seed)
    sku_by = {s.sku_code: s for s in SKUS}

    demand: list[DemandRow] = []
    on_hand: dict[tuple[str, str], float] = {
        (sku.sku_code, dc.dc_code): sku.base_forecast * 1.6 for sku in SKUS for dc in DCS
    }

    for week in range(1, WEEKS + 1):
        for sku in SKUS:
            for dc in DCS:
                forecast = sku.base_forecast * _season(week)
                if dc.dc_code == "RTM":
                    forecast *= 0.72
                actual = forecast * rng.uniform(0.97, 1.03)
                if (
                    sku.sku_code == "TOR-1"
                    and dc.dc_code == "DAL"
                    and week >= TORIC_LIFT_FROM_WEEK
                ):
                    actual = forecast * (1.0 + TORIC_LIFT)
                incoming = forecast * 0.95
                key = (sku.sku_code, dc.dc_code)
                closing = on_hand[key] + incoming - actual
                on_hand[key] = max(closing, 0.0)
                demand.append(
                    DemandRow(
                        week=week,
                        sku_code=sku.sku_code,
                        dc_code=dc.dc_code,
                        forecast_units=round(forecast, 2),
                        actual_units=round(actual, 2),
                        on_hand=round(on_hand[key], 2),
                        incoming=round(incoming, 2),
                    )
                )

    capacity: list[CapacityRow] = []
    for week in range(1, WEEKS + 1):
        for plant in PLANTS:
            used = plant.hours_per_week * rng.uniform(0.78, 0.88)
            if plant.plant_code == "FTW" and week == FTW_OVERTIME_WEEK:
                used = plant.hours_per_week * 1.14
            capacity.append(
                CapacityRow(
                    week=week,
                    plant_code=plant.plant_code,
                    hours_available=plant.hours_per_week,
                    hours_used=round(used, 2),
                )
            )

    scrap: list[ScrapRow] = []
    for week in range(1, WEEKS + 1):
        for plant in PLANTS:
            for sku in SKUS:
                rate = FAMILY_SCRAP[sku.family]
                units = sku_by[sku.sku_code].base_forecast * 0.45
                if plant.plant_code == "SGP":
                    units *= 0.55
                scrap_units = units * rate
                if (
                    plant.plant_code == "SGP"
                    and sku.sku_code == "TOR-1"
                    and week == SGP_TORIC_SCRAP_WEEK
                ):
                    scrap_units = units * rate * 2.1
                scrap.append(
                    ScrapRow(
                        week=week,
                        plant_code=plant.plant_code,
                        sku_code=sku.sku_code,
                        units=round(units, 2),
                        scrap_units=round(scrap_units, 2),
                    )
                )

    return Snapshot(tuple(demand), tuple(capacity), tuple(scrap))
