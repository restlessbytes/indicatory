import abc
from dataclasses import dataclass, asdict
from datetime import datetime


def calculate_price_spread(ask: float, bid: float) -> tuple[float, float]:
    """Calculate the ask-bid-spread for given ask and bid prices.

    Args:
        ask: Float representing the ask price of an asset.
        bid: Float representing the bid price of an asset.

    Returns:
        Tuple (spread value, spread percentage). ``percentage`` is rounded to 6 decimal points.
    """
    amount = abs(ask - bid)
    mid_point = (ask + bid) / 2.0
    percent = amount / mid_point
    return amount, round(percent, 6)


def calculate_bid_price(ask: float, spread_percent: float) -> float:
    spread_halved = spread_percent / 2.0
    dividend = ask * (1.0 - spread_halved)
    divisor = 1.0 + spread_halved
    return dividend / divisor


def calculate_ask_price(bid: float, spread_percent: float) -> float:
    spread_halved = spread_percent / 2.0
    dividend = bid * (1.0 + spread_halved)
    divisor = 1 - spread_halved
    return dividend / divisor


@dataclass
class Asset:
    symbol: str
    exchange: str

    def to_dict(self) -> dict:
        return asdict(self)


class Price:
    def __init__(
        self,
        date_time: datetime,
        # NOTE If you sell shares, you'll get the bid price
        bid: float | None = None,
        # NOTE If you buy shares, you'll pay the ask price
        ask: float | None = None,
        spread: float | None = None,
    ):
        assert any(
            [bid, ask, spread]
        ), f"Either ask / bid or ask / spread or bid / spread must be specified."
        self._bid = bid
        self._ask = ask
        self._spread = spread
        self.date_time = date_time

    def ask(self) -> float:
        if not self._ask:
            self._ask = calculate_ask_price(bid=self._bid, spread_percent=self._spread)
        return self._ask

    def bid(self) -> float:
        if not self._bid:
            self._bid = calculate_bid_price(ask=self._ask, spread_percent=self._spread)
        return self._bid

    def spread(self) -> float:
        """
        Returns:
            Ask-Bid spread for this price as a percentage.
        """
        if not self._spread:
            _, spread_rel = calculate_price_spread(ask=self._ask, bid=self._bid)
            self._spread = spread_rel
        return self._spread

    def to_dict(self) -> dict:
        result = {
            "ask": self._ask,
            "bid": self._bid,
            "date_time": self.date_time.isoformat(),
        }
        val, pct = calculate_price_spread(ask=self.ask(), bid=self.bid())
        result["spread"] = {"amount": val, "percent": pct}
        return result


class FactorCertPrice:
    def __init__(self, underlying: Price, factor: int = 3):
        self._underlying = underlying
        self._factor = factor

    def underlying(self) -> Price:
        return self._underlying


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


class Position(abc.ABC):
    def __init__(
        self,
        asset: Asset,
        account_size: float,
        opening_price: Price,
        close_price: Price | None = None,
        proportion: float | None = None,
        risk_per_trade: float | None = None,
        risk_per_trade_percent: float | None = None,
        risk_percentage: float | None = None,
    ):
        self.asset: Asset = asset
        self.account_size = account_size
        self.opening_price = opening_price
        self.close_price = close_price
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

    def is_open(self) -> bool:
        return self.close_price is None

    def has_been_closed(self) -> bool:
        return not self.is_open()

    @abc.abstractmethod
    def close(self, price: Price) -> Price:
        pass

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass


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
            asset=asset,
            account_size=account_size,
            opening_price=opening_price,
            close_price=None,
            proportion=proportion,
            risk_per_trade=risk_per_trade,
            risk_percentage=risk_percentage,
            risk_per_trade_percent=risk_per_trade_percent,
        )
        self._fixed_fee = fixed_fee
        self._variable_fee = variable_fee

    def close(self, price: Price) -> Price:
        if self.has_been_closed():
            print(
                f"Position has already been closed: {self.close_price.bid:.2f} "
                f"at {self.close_price.date_time.isoformat()}"
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
        gains_losses = (self.shares() * self.close_price.bid()) - self.size()
        gains_losses_percent = gains_losses / self.size()
        gains_losses_final = gains_losses - self.total_cost()[2]
        return (
            round(gains_losses, 3),
            round(gains_losses_percent, 3),
            round(gains_losses_final, 3),
        )

    def shares(self) -> int:
        """
        Returns:
            Number of shares in this position.
        """
        max_size = self.risk_per_trade / self.risk_percentage
        return int(max_size / self.opening_price.ask())

    def size(self) -> float:
        """
        Returns:
            The value of this position at the time of opening.
        """
        return self.shares() * self.opening_price.ask()

    def stop_loss(self) -> float:
        """
        Returns:
            The price that, when reached, closes this position in order to keep losses at a minimum.
        """
        return round(self.opening_price.ask() * (1.0 - self.risk_percentage), 3)

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
            order_volume=self.shares() * self.close_price.bid(),
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


class FactorLongPosition(LongPosition):
    def __init__(
        self,
        asset: Asset,
        account_size: float,
        opening_price: Price,
        factor: int = 3,
        subscription_ratio: float = 0.1,
        proportion: float | None = None,
        risk_per_trade: float | None = None,
        risk_per_trade_percent: float | None = None,
        risk_percentage: float | None = None,
        fixed_fee: float = 0.0,
        variable_fee: float = 0.0,
    ):
        # opening_price refers to the price of the underlying!
        super().__init__(
            asset=asset,
            account_size=account_size,
            opening_price=opening_price,
            proportion=proportion,
            risk_per_trade=risk_per_trade,
            risk_per_trade_percent=risk_per_trade_percent,
            risk_percentage=risk_percentage,
            fixed_fee=fixed_fee,
            variable_fee=variable_fee,
        )
        self.factor = factor
        self._subscription_ratio = subscription_ratio

    def shares(self) -> int:
        investment = self.risk_per_trade / self.risk_percentage
        return int(investment / (self.opening_price.ask() * self._subscription_ratio))

    def size(self) -> float:
        return self.shares() * self.opening_price.ask() * self._subscription_ratio

    def stop_loss(self) -> float:
        risk_percentage_adjusted = self.risk_percentage / self.factor
        return round(self.opening_price.ask() * (1.0 - risk_percentage_adjusted), 3)

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
        gains_losses = (
            (self.close_price.bid() - self.opening_price.ask())
            * self.shares()
            * self._subscription_ratio
            * self.factor
        )
        gains_losses_percent = gains_losses / self.size()
        gains_losses_final = gains_losses - self.total_cost()[2]
        return (
            round(gains_losses, 3),
            round(gains_losses_percent, 3),
            round(gains_losses_final, 3),
        )

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
            order_volume=self.shares()
            * self.close_price.bid()
            * self._subscription_ratio,
        )
        return fees.fixed_fee(), fees.variable_fee(), fees.total()

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["factor"] = self.factor
        result["subscription ratio"] = self._subscription_ratio
        result["risk percentage adjusted"] = self.risk_percentage / self.factor
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
    factor: int | None = None,
    subscription_ratio: float | None = None,
    risk_percentage: float | None = None,
    risk_per_trade: float | None = None,
    risk_per_trade_percent: float | None = None,
    fixed_fee: float = 0.0,
    variable_fee: float = 0.0,
) -> LongPosition:
    if factor and subscription_ratio:
        return FactorLongPosition(
            account_size=account_size,
            asset=asset,
            opening_price=price,
            factor=factor,
            subscription_ratio=subscription_ratio,
            fixed_fee=fixed_fee,
            variable_fee=variable_fee,
            risk_percentage=risk_percentage,
            risk_per_trade=risk_per_trade,
            risk_per_trade_percent=risk_per_trade_percent,
        )
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
    risk_percentage = base_risk_percentage + price.spread()
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
    if price.ask() <= stop_loss:
        raise ValueError("Stop loss cannot be greater or equal to the ask price")
    if price.bid() <= stop_loss < price.ask():
        raise ValueError(
            "Stop loss is between bid and ask and will be knocked out immediately"
        )
    risk_percentage = 1 - (stop_loss / price.ask())
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
