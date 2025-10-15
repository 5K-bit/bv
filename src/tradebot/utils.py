from __future__ import annotations
import re
from typing import Optional, Tuple

PAIR_REGEXES = [
    re.compile(r"([A-Z]{2,5})\s*[-/]\s*([A-Z]{2,5})", re.I),     # e.g., BTC/USD or BTC-USD
    re.compile(r"\b([A-Z]{2,5})(USD|USDT|EUR|GBP|ETH|BTC)\b", re.I),  # e.g., BTCUSD
]


def normalize_symbol(symbol: str) -> str:
    return symbol.replace(" ", "").replace("-", "/").upper()


def extract_pair_and_price(text: str) -> Tuple[Optional[str], Optional[float]]:
    """Extract a trading pair and a price-like number from arbitrary text.

    Returns (pair, price) where either can be None if not found.
    """
    if not text:
        return None, None

    # Find pair
    pair: Optional[str] = None
    for rx in PAIR_REGEXES:
        m = rx.search(text)
        if m:
            if rx is PAIR_REGEXES[0]:
                base, quote = m.group(1), m.group(2)
                pair = f"{base}/{quote}".upper()
            else:
                base, quote = m.group(1), m.group(2)
                pair = f"{base}/{quote}".upper()
            break

    # Find price-like number; prefer a number with decimals and 2-8 digits before/after
    price: Optional[float] = None
    number_matches = re.findall(r"(?<![A-Za-z])\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?|\d+\.\d+", text)
    if number_matches:
        # Clean and parse the first plausible number
        for candidate in number_matches:
            cleaned = candidate.replace(",", "").replace(" ", "")
            try:
                value = float(cleaned)
                if value > 0:
                    price = value
                    break
            except ValueError:
                continue

    return pair, price
