# Trading Bot Scaffold

A Python-based bot that can parse screenshots of exchange tickers (e.g., Kraken or Uphold), extract trading pair and price, fetch live quotes, simulate trades (paper), and place live orders on Kraken (respects DRY_RUN by default). Uphold live trading is scaffolded but not implemented.

## Features
- OCR parsing from screenshots via Tesseract (`pytesseract`) to infer pair and price
- Paper trading simulator with balances and market/limit order support
- Kraken REST client: ticker and AddOrder (with authentication)
- Uphold client: ticker and trade stub
- Typer CLI: `parse`, `ticker`, `trade`, `quick`

## Requirements
- Python 3.10+
- Tesseract OCR binary installed on your system (for OCR commands)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your keys and preferences
```

## Usage
- Parse image for pair/price:
```bash
python -m tradebot.cli parse path/to/screenshot.png
```
- Get ticker:
```bash
EXCHANGE=kraken python -m tradebot.cli ticker BTC/USD
```
- Paper trade:
```bash
EXCHANGE=paper DRY_RUN=false python -m tradebot.cli trade BTC/USD buy 0.01 65000
```
- Quick from image and trade market:
```bash
EXCHANGE=kraken DRY_RUN=true python -m tradebot.cli quick path/to/screenshot.png buy 0.001
```

## Notes
- Kraken live trading requires funded account and API keys with trading scope.
- `DRY_RUN=true` by default to prevent accidental live orders. Set `DRY_RUN=false` to enable.
- OCR quality depends on screenshot clarity; you can pass the pair explicitly to `ticker`/`trade` commands if OCR is uncertain.
