from __future__ import annotations
from typing import Any, Dict, Optional

import httpx

from ..config import config
from .base import OrderResult


API_BASE = "https://api.uphold.com/v0"


class UpholdClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or config.uphold_api_token
        self._session = httpx.Client(base_url=API_BASE, timeout=15.0)

    def _auth_headers(self) -> Dict[str, str]:
        if not self.token:
            raise RuntimeError("Uphold API token missing")
        return {"Authorization": f"Bearer {self.token}"}

    def get_ticker_price(self, pair: str) -> float:
        # Uphold uses dash in pair names like BTC-USD
        p = pair.upper().replace("/", "-")
        resp = self._session.get(f"/ticker/{p}")
        resp.raise_for_status()
        data = resp.json()
        # API may return a list of tickers; try extracting ask/bid average.
        if isinstance(data, list) and data:
            item = data[0]
        else:
            item = data
        bid = float(item.get("bid") or item.get("ask") or item.get("price"))
        ask = float(item.get("ask") or item.get("bid") or item.get("price"))
        return (bid + ask) / 2.0

    def place_order(self, pair: str, side: str, volume: float, price: Optional[float] = None) -> OrderResult:
        # Full Uphold trade flow involves creating transactions on cards.
        # Provide a stub that documents the intended request and respects DRY_RUN.
        request = {
            "pair": pair,
            "side": side,
            "volume": volume,
            "price": price,
        }
        if config.dry_run:
            return OrderResult(order_id=None, executed=False, message="DRY_RUN enabled - Uphold order not placed", raw={"request": request})
        raise NotImplementedError("Uphold live trading is not implemented in this scaffold.")
