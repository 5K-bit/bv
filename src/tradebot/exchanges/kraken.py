from __future__ import annotations
import base64
import hashlib
import hmac
import time
from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import config
from .base import OrderResult


API_BASE = "https://api.kraken.com"


def _kraken_nonce() -> str:
    return str(int(time.time() * 1000))


def _sign_kraken(path: str, data: Dict[str, Any], secret_b64: str) -> str:
    post_data = httpx.QueryParams(data).encode("utf-8")
    nonce = data.get("nonce", "")
    sha256 = hashlib.sha256((nonce + post_data.decode()).encode()).digest()
    message = path.encode() + sha256
    mac = hmac.new(base64.b64decode(secret_b64), message, hashlib.sha512)
    sig_digest = base64.b64encode(mac.digest()).decode()
    return sig_digest


class KrakenClient:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> None:
        self.api_key = api_key or config.kraken_api_key
        self.api_secret = api_secret or config.kraken_api_secret
        self._session = httpx.Client(base_url=API_BASE, timeout=15.0)
        self._pair_cache: Dict[str, str] = {}

    @retry(wait=wait_exponential(min=0.5, max=5), stop=stop_after_attempt(3))
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self._session.get(path, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(f"Kraken error: {data['error']}")
        return data["result"]

    @retry(wait=wait_exponential(min=0.5, max=5), stop=stop_after_attempt(3))
    def _post_private(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Kraken API credentials missing")
        url_path = f"/0/private/{path}"
        data = {**data, "nonce": _kraken_nonce()}
        signature = _sign_kraken(url_path, data, self.api_secret)
        headers = {
            "API-Key": self.api_key,
            "API-Sign": signature,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = self._session.post(url_path, data=data, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(f"Kraken error: {data['error']}")
        return data["result"]

    def _map_pair(self, pair: str) -> str:
        p = pair.upper().replace("-", "/").replace(" ", "")
        if p in self._pair_cache:
            return self._pair_cache[p]
        # Fetch AssetPairs and map altname -> wsname
        result = self._get("/0/public/AssetPairs")
        mapping: Dict[str, str] = {}
        for code, meta in result.items():
            alt = meta.get("altname")
            ws = meta.get("wsname")
            if alt and ws:
                mapping[ws.upper()] = alt
        # Heuristic: also try without slash in wsname
        p_no_slash = p.replace("/", "")
        alt = mapping.get(p) or mapping.get(p_no_slash)
        if not alt:
            # fallback: try directly; Kraken might accept altname already
            alt = p_no_slash
        self._pair_cache[p] = alt
        return alt

    def get_ticker_price(self, pair: str) -> float:
        kpair = self._map_pair(pair)
        result = self._get("/0/public/Ticker", params={"pair": kpair})
        # result keys can be arbitrary; take first
        first = next(iter(result.values()))
        last_trade = first.get("c", [None])[0]
        if last_trade is None:
            raise RuntimeError("No last trade price in Kraken response")
        return float(last_trade)

    def place_order(self, pair: str, side: str, volume: float, price: Optional[float] = None) -> OrderResult:
        if side.lower() not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")
        kpair = self._map_pair(pair)
        data = {
            "ordertype": "market" if price is None else "limit",
            "type": side.lower(),
            "volume": str(volume),
            "pair": kpair,
        }
        if price is not None:
            data["price"] = str(price)
        # For safety, enforce dry-run default
        if config.dry_run:
            return OrderResult(order_id=None, executed=False, message="DRY_RUN enabled - not placing order", raw={"request": data})
        result = self._post_private("AddOrder", data)
        descr = result.get("descr", {})
        txid = None
        if isinstance(result.get("txid"), list) and result["txid"]:
            txid = result["txid"][0]
        return OrderResult(order_id=txid, executed=True, message=str(descr), raw=result)
