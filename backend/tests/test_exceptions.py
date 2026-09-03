from app.catalog import CURRENT_WEEK, PLANTS, SKUS
from app.exceptions import BIAS, OVERTIME, SCRAP, STOCKOUT, rank_exceptions
from app.generate import generate_snapshot


def test_planted_week_12_queue_contains_the_three_shocks():
    items = rank_exceptions(generate_snapshot(), CURRENT_WEEK)
    kinds = {e.kind for e in items}
    assert STOCKOUT in kinds
    assert OVERTIME in kinds
    assert SCRAP in kinds
    assert BIAS in kinds


def test_dallas_toric_bias_is_positive_underforecast():
    items = rank_exceptions(generate_snapshot(), CURRENT_WEEK)
    toric = next(e for e in items if e.kind == BIAS and e.sku_code == "TOR-1" and e.dc_code == "DAL")
    assert "under-forecast" in toric.title
    assert toric.action == "hold_registry_promotion"


def test_fort_worth_overtime_prices_extra_hours():
    items = rank_exceptions(generate_snapshot(), CURRENT_WEEK)
    ftw = next(e for e in items if e.kind == OVERTIME and e.plant_code == "FTW")
    plant = next(p for p in PLANTS if p.plant_code == "FTW")
    extra = 80.0 * 1.14 - 80.0
    assert ftw.dollar_impact == round(extra * plant.overtime_usd_per_hour, 2)


def test_singapore_toric_scrap_beats_the_family_baseline():
    items = rank_exceptions(generate_snapshot(), CURRENT_WEEK)
    scrap = next(e for e in items if e.kind == SCRAP and e.plant_code == "SGP" and e.sku_code == "TOR-1")
    assert scrap.dollar_impact > 0
    assert scrap.action == "hold_run_inspect_lot"


def test_queue_is_sorted_by_dollar_impact():
    items = rank_exceptions(generate_snapshot(), CURRENT_WEEK)
    dollars = [e.dollar_impact for e in items]
    assert dollars == sorted(dollars, reverse=True)
    assert items[0].dollar_impact >= items[-1].dollar_impact


def test_stockout_dollars_are_gap_times_penalty():
    snap = generate_snapshot()
    items = [e for e in rank_exceptions(snap, CURRENT_WEEK) if e.kind == STOCKOUT]
    assert items
    sku_by = {s.sku_code: s for s in SKUS}
    week_rows = [r for r in snap.demand if r.week == CURRENT_WEEK]
    for exc in items:
        row = next(r for r in week_rows if r.sku_code == exc.sku_code and r.dc_code == exc.dc_code)
        gap = row.forecast_units * 2.0 - (row.on_hand + row.incoming)
        assert gap > 0
        assert exc.dollar_impact == round(gap * sku_by[row.sku_code].stockout_penalty, 2)
