import pytest

from indicatory.position import (
    Position,
    check_position_spec,
    calculate_price_spread,
    calculate_ask_price,
    calculate_bid_price,
)


ACCOUNT_SIZE = 50_000
PROPOSITION = 6250.0
RISK_PER_TRADE = 500.0
RISK_PERCENTAGE = 0.08
RISK_PER_TRADE_PERCENT = 0.01


def test_price_spreads():
    ask = 100.0
    bid = 98.0
    spread_abs, spread_rel = calculate_price_spread(ask=ask, bid=bid)
    spread_rel_rounded = round(spread_rel, 4)
    assert int(spread_abs) == 2
    assert spread_rel_rounded == 0.0202

    assert calculate_ask_price(bid=bid, spread_percent=spread_rel)
    assert calculate_bid_price(ask=ask, spread_percent=spread_rel)


@pytest.mark.parametrize(
    "prop, rpt, rp, p, error",
    [
        (False, False, False, False, ValueError),
        (False, False, False, True, ValueError),
        (False, False, True, False, ValueError),
        (False, False, True, True, None),
        (False, True, False, False, ValueError),
        (False, True, False, True, ValueError),
        (False, True, True, False, None),
        (False, True, True, True, None),
        (True, False, False, False, ValueError),
        (True, False, False, True, None),
        (True, False, True, False, None),
        (True, False, True, True, None),
        (True, True, False, False, None),
        (True, True, False, True, None),
        (True, True, True, False, None),
        (True, True, True, True, None),
    ],
)
def test_position_spec(prop, rpt, rp, p, error):
    prop = PROPOSITION if prop else None
    rpt = RISK_PER_TRADE if rpt else None
    rp = RISK_PERCENTAGE if rp else None
    p = RISK_PER_TRADE_PERCENT if p else None
    if error is not None:
        with pytest.raises(error):
            check_position_spec(
                account_size=ACCOUNT_SIZE,
                proportion=prop,
                risk_per_trade=rpt,
                risk_percentage=rp,
                risk_per_trade_percent=p,
            )
    else:
        result = check_position_spec(
            account_size=ACCOUNT_SIZE,
            proportion=prop,
            risk_per_trade=rpt,
            risk_percentage=rp,
            risk_per_trade_percent=p,
        )
        assert result == (
            PROPOSITION,
            RISK_PER_TRADE,
            RISK_PERCENTAGE,
            RISK_PER_TRADE_PERCENT,
        )
