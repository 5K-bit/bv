from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import random


@dataclass
class SimulatedPosition:
    base: float
    quote: float


class PaperExchange:
    def __init__(self, base_currency: str = "USD") -> None:
        self.base_currency = base_currency.upper()
        self.balances: Dict[str, float] = {self.base_currency: 10000.0}
        self.prices: Dict[str, float] = {}

    def set_price(self, pair: str, price: float) -> None:
        self.prices[pair.upper().replace("-", "/")] = price

    def get_ticker_price(self, pair: str) -> float:
        p = pair.upper().replace("-", "/")
        if p not in self.prices:
            # generate a random price in a reasonable range
            base, quote = p.split("/")
            seed = sum(ord(c) for c in base) + sum(ord(c) for c in quote)
            random.seed(seed)
            self.prices[p] = round(random.uniform(10, 50000), 2)
        return self.prices[p]

    def ensure_asset(self, asset: str) -> None:
        self.balances.setdefault(asset.upper(), 0.0)

    def place_order(self, pair: str, side: str, volume: float, price: float | None = None) -> Tuple[bool, str]:
        p = pair.upper().replace("-", "/")
        base, quote = p.split("/")
        self.ensure_asset(base)
        self.ensure_asset(quote)
        market_price = self.get_ticker_price(p)
        exec_price = market_price if price is None else price

        if side.lower() == "buy":
            cost = volume * exec_price
            if self.balances[quote] + 1e-8 < cost:
                return False, "Insufficient quote balance"
            self.balances[quote] -= cost
            self.balances[base] += volume
            return True, f"Bought {volume} {base} @ {exec_price}"
        elif side.lower() == "sell":
            if self.balances[base] + 1e-8 < volume:
                return False, "Insufficient base balance"
            proceeds = volume * exec_price
            self.balances[base] -= volume
            self.balances[quote] += proceeds
            return True, f"Sold {volume} {base} @ {exec_price}"
        else:
            return False, "Invalid side"
