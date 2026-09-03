from dataclasses import dataclass


@dataclass(frozen=True)
class SkuSpec:
    sku_code: str
    family: str
    unit_cost: float
    stockout_penalty: float
    base_forecast: float


@dataclass(frozen=True)
class DcSpec:
    dc_code: str
    name: str


@dataclass(frozen=True)
class PlantSpec:
    plant_code: str
    name: str
    hours_per_week: float
    overtime_usd_per_hour: float


SKUS = (
    SkuSpec("DD-1", "Daily Disposable", unit_cost=0.42, stockout_penalty=2.10, base_forecast=4200),
    SkuSpec("TOR-1", "Toric", unit_cost=0.95, stockout_penalty=4.80, base_forecast=1800),
    SkuSpec("IOL-1", "IOL", unit_cost=18.0, stockout_penalty=65.0, base_forecast=220),
)

DCS = (
    DcSpec("DAL", "Dallas"),
    DcSpec("RTM", "Rotterdam"),
)

PLANTS = (
    PlantSpec("FTW", "Fort Worth", hours_per_week=80.0, overtime_usd_per_hour=85.0),
    PlantSpec("SGP", "Singapore", hours_per_week=80.0, overtime_usd_per_hour=72.0),
)

WEEKS = 12
CURRENT_WEEK = 12
COVER_WEEKS = 2.0
BIAS_WEEKS = 8
BIAS_THRESHOLD = 0.12
SCRAP_SPIKE_MULTIPLIER = 1.6
FAMILY_SCRAP = {
    "Daily Disposable": 0.020,
    "Toric": 0.085,
    "IOL": 0.015,
}

# Seeded shocks for the week-12 ranking tests.
TORIC_LIFT_FROM_WEEK = 8
TORIC_LIFT = 0.25
FTW_OVERTIME_WEEK = CURRENT_WEEK
SGP_TORIC_SCRAP_WEEK = CURRENT_WEEK
