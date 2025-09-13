from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class TradeCreatedEvent:
    profile_id: int
    exchange: str
    symbol: str
    amount: float
    buy_price: float
    current_price: float
    profit: float
    timestamp: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_trade(cls, profile_id, exchange, symbol, amount, buy_price, current_price):
        profit = (current_price - buy_price) * amount
        return cls(
            profile_id=profile_id,
            exchange=exchange,
            symbol=symbol,
            amount=amount,
            buy_price=buy_price,
            current_price=current_price,
            profit=profit,
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
        )


@dataclass
class ReportCompletedEvent:
    report_id: int
    profile_id: int
    format: str
    status: str
    file_url: str
    timestamp: str = datetime.now(timezone.utc).isoformat() + "Z"

    def to_dict(self):
        return asdict(self)
