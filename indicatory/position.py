from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Asset:
    symbol: str
    exchange: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Price:
    bid: float
    ask: float
    date_time: datetime

    def spread(self) -> tuple[float, float]:
        amount = abs(self.ask - self.bid)
        percent = round(amount / self.ask, 6)
        return amount, percent

    def to_dict(self) -> dict:
        result = asdict(self)
        result["date_time"] = result["date_time"].isoformat()
        val, pct = self.spread()
        result["spread"] = {"amount": val, "percent": pct}
        return result


@dataclass
class Fees:
    fixed: float
    variable: float
    # 'order volume' = (no. of shares) x (price per share)
    order_volume: float

    def variable_fee(self) -> float:
        return self.order_volume * self.variable

    def fixed_fee(self) -> float:
        return self.fixed

    def total(self) -> float:
        return self.fixed_fee() + self.variable_fee()


def check_position_spec(
    account_size: float,
    proportion: float | None = None,
    risk_per_trade: float | None = None,
    risk_per_trade_percent: float | None = None,
    risk_percentage: float | None = None,
) -> tuple[float, float, float, float]:
    # This reassignment makes calculations a bit easier ;)
    prop, rpt, rp, p = (
        proportion,
        risk_per_trade,
        risk_percentage,
        risk_per_trade_percent,
    )
    spec = [prop, rpt, rp, p]
    spec_config = tuple(map(bool, spec))
    invalid_spec_configs = [
        (False, False, False, False),
        (False, False, False, True),
        (False, False, True, False),
        (False, True, False, False),
        (False, True, False, True),
        (True, False, False, False),
    ]
    if spec_config in invalid_spec_configs:
        raise ValueError(f"Invalid position spec: {tuple(spec)}")
    match spec_config:
        #    ( prop , rpt , rp  , p   )
        case (False, False, True, True):
            prop = (account_size * p) / rp
            rpt = account_size * p
        case (False, True, True, False):
            prop = rpt / rp
            p = rpt / account_size
        case (False, True, True, True):
            prop = rpt / rp
        case (True, False, False, True):
            rpt = account_size * p
            rp = (account_size * p) / prop
        case (True, False, True, False):
            p = (prop * rp) / account_size
            rpt = account_size * p
        case (True, False, True, True):
            rpt = account_size * p
        case (True, True, False, False):
            rp = rpt / prop
            p = rpt / account_size
        case (True, True, False, True):
            rp = rpt / prop
        case (True, True, True, False):
            p = rpt / account_size
        case (True, True, True, True):
            pass
        case _:
            raise ValueError(f"Unexpected position spec: {tuple(spec)} ({spec_config})")
    return prop, rpt, rp, p


class Position:
    def __init__(
        self,
        account_size: float,
        proportion: float | None = None,
        risk_per_trade: float | None = None,
        risk_per_trade_percent: float | None = None,
        risk_percentage: float | None = None,
    ):
        self.account_size = account_size
        prop, rpt, rp, p = check_position_spec(
            account_size=account_size,
            proportion=proportion,
            risk_per_trade=risk_per_trade,
            risk_percentage=risk_percentage,
            risk_per_trade_percent=risk_per_trade_percent,
        )
        self.proportion = prop
        self.risk_per_trade = rpt
        self.risk_percentage = rp
        self.risk_per_trade_percent = p


class LongPosition(Position):
    def __init__(
        self,
        asset: Asset,
        account_size: float,
        opening_price: Price,
        proportion: float | None = None,
        risk_per_trade: float | None = None,
        risk_per_trade_percent: float | None = None,
        risk_percentage: float | None = None,
        fixed_fee: float = 0.0,
        variable_fee: float = 0.0,
    ):
        super().__init__(
            account_size=account_size,
            proportion=proportion,
            risk_per_trade=risk_per_trade,
            risk_percentage=risk_percentage,
            risk_per_trade_percent=risk_per_trade_percent,
        )
        self.asset = asset
        self.opening_price = opening_price
        self.account_size = account_size
        self._fixed_fee = fixed_fee
        self._variable_fee = variable_fee
        self.close_price: Price | None = None

    def is_open(self) -> bool:
        return self.close_price is None

    def has_been_closed(self) -> bool:
        return not self.is_open()

    def close(self, price: Price) -> Price:
        if self.has_been_closed():
            print(
                f"Position has already been closed: {self.close_price.bid:.2f} at {self.close_price.date_time.isoformat()}"
            )
            return self.close_price
        self.close_price = price
        return self.close_price

    def returns(self) -> tuple[float, float, float] | None:
        """
        Returns:
           Tuple representing this position's returns.

           Format: (net gains, net gains (%), net gains - total costs)

           If this position is still open, returns ``None``.
        """
        if self.is_open():
            print("There are no returns yet because position is still open")
            return None
        gains_losses = (self.shares() * self.close_price.bid) - self.size()
        gains_losses_percent = gains_losses / self.size()
        gains_losses_final = gains_losses - self.total_cost()[2]
        return (
            round(gains_losses, 3),
            gains_losses_percent,
            round(gains_losses_final, 3),
        )

    def shares(self) -> int:
        max_size = self.risk_per_trade / self.risk_percentage
        return int(round(max_size / self.opening_price.ask))

    def size(self) -> float:
        return self.shares() * self.opening_price.ask

    def stop_loss(self) -> float:
        return round(self.opening_price.ask * (1.0 - self.risk_percentage), 3)

    def opening_costs(self) -> tuple[float, float, float]:
        """
        Returns:
            Tuple representing fees: (fixed, variable, total)
        """
        fees = Fees(
            fixed=self._fixed_fee, variable=self._variable_fee, order_volume=self.size()
        )
        return fees.fixed_fee(), fees.variable_fee(), fees.total()

    def closing_costs(self) -> tuple[float, float, float] | None:
        """
        Returns:
            Tuple representing fees: (fixed, variable, total), or ``None`` if position hasn't been closed yet.
        """
        if self.is_open():
            return None
        fees = Fees(
            fixed=self._fixed_fee,
            variable=self._variable_fee,
            order_volume=self.shares() * self.close_price.bid,
        )
        return fees.fixed_fee(), fees.variable_fee(), fees.total()

    def total_cost(self) -> tuple[float, float, float]:
        of, ov, ot = self.opening_costs()
        if self.is_open():
            return of, ov, ot
        cf, cv, ct = self.closing_costs()
        return of + cf, ov + cv, ot + ct

    def to_dict(self) -> dict:
        if self.has_been_closed():
            closing_price = self.close_price.to_dict()
            closing_costs = _costs_dict(self.closing_costs())
            status = "closed"
            net, net_pct, final = self.returns()
            returns = {"net": net, "net percent": net_pct, "final": final}
            days_till_close = (
                self.close_price.date_time - self.opening_price.date_time
            ).days
        else:
            closing_price = {}
            closing_costs = {}
            status = "open"
            returns = {}
            days_till_close = None
        costs = {
            "fees": {"fixed": self._fixed_fee, "variable": self._variable_fee},
            "opening": _costs_dict(self.opening_costs()),
            "closing": closing_costs,
            "total": _costs_dict(self.total_cost()),
        }
        result = {
            "asset": self.asset.to_dict(),
            "opening price": self.opening_price.to_dict(),
            "closing price": closing_price,
            "account size": self.account_size,
            "position size": self.size(),
            "number of shares": self.shares(),
            "stop-loss": self.stop_loss(),
            "status": status,
            "risk per trade": {
                "amount": self.risk_per_trade,
                "percent": self.risk_per_trade_percent,
            },
            "risk percentage": self.risk_percentage,
            "costs": costs,
            "returns": returns,
            "days till close": days_till_close,
        }
        return result


def _costs_dict(costs: tuple[float, float, float]) -> dict[str, float]:
    fixed, variable, total = costs
    return {"fixed": fixed, "variable": variable, "total": total}


def print_position_info(position: Position):
    # TODO
    raise NotImplementedError()


def open_long(
    account_size: float,
    asset: Asset,
    price: Price,
    risk_percentage: float | None = None,
    risk_per_trade: float | None = None,
    risk_per_trade_percent: float | None = None,
    fixed_fee: float = 0.0,
    variable_fee: float = 0.0,
) -> LongPosition:
    return LongPosition(
        account_size=account_size,
        asset=asset,
        opening_price=price,
        fixed_fee=fixed_fee,
        variable_fee=variable_fee,
        risk_percentage=risk_percentage,
        risk_per_trade=risk_per_trade,
        risk_per_trade_percent=risk_per_trade_percent,
    )


def open_long_spread_aware(
    account_size: float,
    asset: Asset,
    price: Price,
    base_risk_percentage: float,
    fixed_fee: float = 0.0,
    variable_fee: float = 0.0,
    risk_per_trade: float | None = None,
    risk_per_trade_percent: float | None = None,
) -> LongPosition:
    risk_percentage = base_risk_percentage + price.spread()[1]
    return LongPosition(
        account_size=account_size,
        asset=asset,
        opening_price=price,
        fixed_fee=fixed_fee,
        variable_fee=variable_fee,
        risk_percentage=risk_percentage,
        risk_per_trade=risk_per_trade,
        risk_per_trade_percent=risk_per_trade_percent,
    )


def open_long_with_stop_loss(
    account_size: float,
    asset: Asset,
    price: Price,
    stop_loss: float,
    fixed_fee: float = 0.0,
    variable_fee: float = 0.0,
    risk_per_trade: float | None = None,
    risk_per_trade_percent: float | None = None,
) -> LongPosition:
    if price.ask <= stop_loss:
        raise ValueError("Stop loss cannot be greater or equal to the ask price")
    if price.bid <= stop_loss < price.ask:
        raise ValueError(
            "Stop loss is between bid and ask and will be knocked out immediately"
        )
    risk_percentage = 1 - (stop_loss / price.ask)
    return LongPosition(
        account_size=account_size,
        asset=asset,
        opening_price=price,
        fixed_fee=fixed_fee,
        variable_fee=variable_fee,
        risk_percentage=risk_percentage,
        risk_per_trade=risk_per_trade,
        risk_per_trade_percent=risk_per_trade_percent,
    )
