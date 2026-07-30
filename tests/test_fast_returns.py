"""Equivalence tests: fast_returns (vectorized) vs analytics (per investor).

The legacy per-investor functions are used as the oracle: for each investor
in a synthetic dataset covering partial sells, coupons, price gaps, missing
prices and deposit/withdrawal operations, the bulk results must match.
"""

import unittest
from datetime import date

from tesouro_direto_fetcher import _HAS_ANALYSIS

if not _HAS_ANALYSIS:
    raise unittest.SkipTest("Analysis extras required.")

import polars as pl
import pytest
from tesouro_direto_fetcher import analytics, fast_returns
from tesouro_direto_fetcher.constants import Column as C

INV = C.INVESTOR_ID.value
BT = C.BOND_TYPE.value
MAT = C.MATURITY_DATE.value
OP_DATE = C.OPERATION_DATE.value
OP_TYPE = C.OPERATION_TYPE.value
QTY = C.QUANTITY.value
BOND_VALUE = C.BOND_VALUE.value
OP_VALUE = C.OPERATION_VALUE.value
REF = C.REFERENCE_DATE.value
SELL_PRICE = C.SELL_PRICE.value
CPN_DATE = C.BUYBACK_DATE.value
UNIT = C.UNIT_PRICE.value

CURRENT_DATE = date(2024, 6, 15)

SELIC = ("Tesouro Selic", date(2030, 3, 1))
IPCA = ("Tesouro IPCA+ com Juros Semestrais", date(2035, 5, 15))
NOPRICE = ("Tesouro Prefixado", date(2031, 1, 1))


def _op(inv, d, bond, qty, value, op_type):
    return {
        INV: inv,
        OP_DATE: d,
        BT: bond[0],
        MAT: bond[1],
        QTY: float(qty),
        BOND_VALUE: float(value) / float(qty) if qty else 0.0,
        OP_VALUE: float(value),
        OP_TYPE: op_type,
    }


@pytest.fixture(scope="module")
def operations() -> pl.DataFrame:
    rows = [
        # Investor 1: two buys, one partial sell crossing both lots
        _op(1, date(2024, 1, 10), SELIC, 10, 1000.0, "C"),
        _op(1, date(2024, 2, 15), SELIC, 5, 550.0, "C"),
        _op(1, date(2024, 3, 5), SELIC, 12, 1350.0, "V"),
        # Investor 2: open position with coupons, plus a bond without prices
        _op(2, date(2024, 1, 20), IPCA, 4, 4000.0, "C"),
        _op(2, date(2024, 2, 10), NOPRICE, 2, 1500.0, "C"),
        # Investor 3: deposits/withdrawals mixed with a buy
        _op(3, date(2024, 2, 5), SELIC, 3, 315.0, "C"),
        _op(3, date(2024, 1, 15), SELIC, 1, 100.0, "D"),
        _op(3, date(2024, 4, 2), SELIC, 1, 105.0, "R"),
        # Investor 4: sells more than bought (degenerate data)
        _op(4, date(2024, 1, 8), SELIC, 2, 200.0, "C"),
        _op(4, date(2024, 2, 20), SELIC, 5, 540.0, "V"),
        _op(4, date(2024, 3, 12), SELIC, 3, 320.0, "C"),
    ]
    return pl.DataFrame(rows)


@pytest.fixture(scope="module")
def prices() -> pl.DataFrame:
    def _price(d, bond, p):
        return {REF: d, BT: bond[0], MAT: bond[1], SELL_PRICE: p}

    rows = []
    # Selic: monthly prices Jan-Jun (day 1 and day 18)
    selic_prices = [100.0, 104.0, 109.0, 112.0, 116.0, 118.0]
    for month, p in enumerate(selic_prices, start=1):
        rows.append(_price(date(2024, month, 1), SELIC, p))
        rows.append(_price(date(2024, month, 18), SELIC, p + 1.5))
    # IPCA: prices with a gap in March (carry-forward path)
    for month, p in [(1, 1000.0), (2, 1010.0), (4, 1035.0), (5, 1042.0), (6, 1050.0)]:
        rows.append(_price(date(2024, month, 12), IPCA, p))
    # NOPRICE bond intentionally has no price rows
    return pl.DataFrame(rows)


@pytest.fixture(scope="module")
def coupons() -> pl.DataFrame:
    rows = [
        {BT: IPCA[0], MAT: IPCA[1], CPN_DATE: date(2024, 2, 15), UNIT: 30.0},
        {BT: IPCA[0], MAT: IPCA[1], CPN_DATE: date(2024, 5, 15), UNIT: 31.0},
        # Coupon before any holding (must not count)
        {BT: IPCA[0], MAT: IPCA[1], CPN_DATE: date(2023, 11, 16), UNIT: 29.0},
    ]
    return pl.DataFrame(rows)


def _legacy_lots(operations, prices, coupons, investor):
    inv_ops = operations.filter(pl.col(INV) == investor)
    return analytics.calculate_operations_returns(
        inv_ops, prices, current_date=CURRENT_DATE, coupons=coupons
    )


LOT_METRICS = [
    QTY,
    OP_VALUE,
    "sell_value",
    "total_coupons",
    "end_value",
    "simple_return",
    "annualized_return",
    "holding_days",
]


def _sorted_lots(df: pl.DataFrame) -> list[dict]:
    return (
        df.select([BT, OP_DATE, "status"] + LOT_METRICS)
        .with_columns(pl.col(OP_DATE).cast(pl.Date))
        .sort([BT, OP_DATE, "status", QTY])
        .to_dicts()
    )


@pytest.mark.parametrize("investor", [1, 2, 3, 4])
def test_lots_match_legacy(operations, prices, coupons, investor):
    legacy = _legacy_lots(operations, prices, coupons, investor)
    fast = fast_returns.calculate_lots_bulk(
        operations, prices, coupons=coupons, current_date=CURRENT_DATE
    ).filter(pl.col(INV) == investor)

    assert fast.height == legacy.height
    for fast_row, legacy_row in zip(
        _sorted_lots(fast), _sorted_lots(legacy), strict=True
    ):
        for col in LOT_METRICS:
            assert fast_row[col] == pytest.approx(
                legacy_row[col], rel=1e-9, abs=1e-9
            ), f"investor={investor} col={col}"
        assert fast_row["status"] == legacy_row["status"]


MONTHLY_METRICS = [
    "monthly_return",
    "cumulative_return",
    "portfolio_value",
    "net_cash_flow",
]


@pytest.mark.parametrize("investor", [1, 2, 3, 4])
def test_monthly_returns_match_legacy(operations, prices, coupons, investor):
    inv_ops = operations.filter(pl.col(INV) == investor)
    legacy = analytics.calculate_portfolio_monthly_returns(
        inv_ops, prices, coupons=coupons
    )
    fast = fast_returns.calculate_monthly_returns_bulk(
        operations, prices, coupons=coupons
    ).filter(pl.col(INV) == investor)

    assert fast.height == legacy.height
    for fast_row, legacy_row in zip(
        fast.sort("month").to_dicts(), legacy.sort("month").to_dicts(), strict=True
    ):
        assert fast_row["month"] == legacy_row["month"]
        for col in MONTHLY_METRICS:
            assert fast_row[col] == pytest.approx(
                legacy_row[col], rel=1e-9, abs=1e-9
            ), f"investor={investor} month={fast_row['month']} col={col}"


@pytest.mark.parametrize("investor", [1, 2, 3, 4])
def test_monthly_returns_by_bond_type_match_legacy(
    operations, prices, coupons, investor
):
    inv_ops = operations.filter(pl.col(INV) == investor)
    fast = fast_returns.calculate_monthly_returns_bulk(
        operations, prices, coupons=coupons, by_bond_type=True
    ).filter(pl.col(INV) == investor)

    for bond_type in inv_ops[BT].unique().to_list():
        bt_ops = inv_ops.filter(pl.col(BT) == bond_type)
        bt_prices = prices.filter(pl.col(BT) == bond_type)
        legacy = analytics.calculate_portfolio_monthly_returns(
            bt_ops, bt_prices, coupons=coupons.filter(pl.col(BT) == bond_type)
        )
        fast_bt = fast.filter(pl.col(BT) == bond_type)

        if legacy.height == 0:
            # Legacy returns nothing when the bond has no prices at all;
            # the bulk version still emits (zero-valued) months.
            continue
        assert fast_bt.height == legacy.height
        for fast_row, legacy_row in zip(
            fast_bt.sort("month").to_dicts(),
            legacy.sort("month").to_dicts(),
            strict=True,
        ):
            assert fast_row["month"] == legacy_row["month"]
            for col in MONTHLY_METRICS:
                assert fast_row[col] == pytest.approx(
                    legacy_row[col], rel=1e-9, abs=1e-9
                ), f"investor={investor} bond={bond_type} col={col}"


def test_summary_matches_legacy_aggregates(operations, prices, coupons):
    lots = fast_returns.calculate_lots_bulk(
        operations, prices, coupons=coupons, current_date=CURRENT_DATE
    )
    counts = operations.group_by(INV).len(name="num_operations")
    summary, by_bond = fast_returns.summarize_lots(lots, counts)

    for investor in [1, 2, 3, 4]:
        legacy = _legacy_lots(operations, prices, coupons, investor)
        row = summary.filter(pl.col(INV) == investor).to_dicts()[0]
        assert row["total_invested"] == pytest.approx(
            float(legacy[OP_VALUE].sum()), rel=1e-9
        )
        assert row["total_end_value"] == pytest.approx(
            float(legacy["end_value"].sum()), rel=1e-9
        )
        assert (
            row["num_operations"] == operations.filter(pl.col(INV) == investor).height
        )

    assert by_bond.filter(pl.col(INV) == 2).height == 2


def test_empty_inputs():
    empty = pl.DataFrame()
    prices = pl.DataFrame(
        {REF: [date(2024, 1, 1)], BT: ["X"], MAT: [date(2030, 1, 1)], SELL_PRICE: [1.0]}
    )
    assert fast_returns.calculate_lots_bulk(empty, prices).height == 0
    assert fast_returns.calculate_monthly_returns_bulk(empty, prices).height == 0
