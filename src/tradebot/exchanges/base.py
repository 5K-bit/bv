from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any


@dataclass
class OrderResult:
    order_id: Optional[str]
    executed: bool
    message: str
    raw: Dict[str, Any]


class ExchangeClient(Protocol):
    def get_ticker_price(self, pair: str) -> float:  # raises on failure
        ...

    def place_order(self, pair: str, side: str, volume: float, price: Optional[float] = None) -> OrderResult:
        ...
