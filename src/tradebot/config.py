from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class AppConfig:
    exchange: str = os.getenv("EXCHANGE", "kraken").lower()
    dry_run: bool = get_bool("DRY_RUN", True)
    base_currency: str = os.getenv("BASE_CURRENCY", "USD").upper()

    # Kraken
    kraken_api_key: Optional[str] = os.getenv("KRAKEN_API_KEY")
    kraken_api_secret: Optional[str] = os.getenv("KRAKEN_API_SECRET")

    # Uphold
    uphold_api_token: Optional[str] = os.getenv("UPHOLD_API_TOKEN")


config = AppConfig()
