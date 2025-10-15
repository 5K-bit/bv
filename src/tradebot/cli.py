from __future__ import annotations
import sys
from typing import Optional
import typer
from rich import print

from .config import config
from .ocr import parse_pair_and_price_from_image, OCRUnavailableError
from .exchanges.kraken import KrakenClient
from .exchanges.uphold import UpholdClient
from .simulator import PaperExchange

app = typer.Typer(add_completion=False)


def get_client():
    if config.exchange == "kraken":
        return KrakenClient()
    if config.exchange == "uphold":
        return UpholdClient()
    if config.exchange == "paper":
        return PaperExchange()
    raise typer.BadParameter(f"Unknown EXCHANGE: {config.exchange}")


@app.command()
def parse(image: str):
    """Parse a screenshot to extract [pair, price] and show OCR text."""
    try:
        pair, price, text = parse_pair_and_price_from_image(image)
    except OCRUnavailableError as e:
        print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    print({"pair": pair, "price": price})
    print("\n[dim]OCR text:[/dim]\n")
    print(text)


@app.command()
def ticker(pair: str):
    """Get last trade price for a pair from selected exchange."""
    client = get_client()
    price = client.get_ticker_price(pair)
    print({"pair": pair.upper(), "price": price})


@app.command()
def trade(pair: str, side: str, volume: float, price: Optional[float] = None):
    """Place a trade on the configured exchange (respects DRY_RUN)."""
    client = get_client()
    if hasattr(client, "place_order"):
        result = client.place_order(pair, side, volume, price)  # type: ignore
        print(result)
    else:
        print("Client does not support trading")


@app.command()
def quick(image: str, side: str, volume: float):
    """Quick-trade: parse pair/price from screenshot, show ticker, and trade."""
    try:
        pair, parsed_price, _ = parse_pair_and_price_from_image(image)
    except OCRUnavailableError as e:
        print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    if not pair:
        print("[red]Could not extract pair from image[/red]")
        raise typer.Exit(code=2)

    client = get_client()
    live_price = client.get_ticker_price(pair)
    print({"pair": pair, "parsed_price": parsed_price, "live_price": live_price})

    # Place market order by default
    result = client.place_order(pair, side, volume)
    print(result)


if __name__ == "__main__":
    app()
