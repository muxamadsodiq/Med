# Med – Trending Signal Channel for Telegram

A Python Telegram bot that scans a configurable watchlist of crypto / stock tickers, generates
**buy / sell signals** using technical analysis, and broadcasts them to a Telegram channel at a
scheduled interval.

---

## Features

| Feature | Detail |
|---|---|
| **Technical indicators** | RSI, MACD, Bollinger Bands, EMA crossover |
| **Signal strength scoring** | 0 – 100 % composite score per asset |
| **Automatic channel broadcast** | Configurable interval (default 30 min) |
| **Bot commands** | `/start`, `/signals`, `/watchlist`, `/help` |
| **Customisable watchlist** | Crypto or stock tickers via `.env` |

---

## Quick Start

### 1 – Prerequisites

* Python 3.11+
* A Telegram bot token from [@BotFather](https://t.me/BotFather)
* The bot added as an **admin** to the target Telegram channel

### 2 – Clone & install

```bash
git clone https://github.com/muxamadsodiq/Med.git
cd Med
pip install -r requirements.txt
```

### 3 – Configure

```bash
cp .env.example .env
# Edit .env and fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID
```

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | *required* |
| `TELEGRAM_CHANNEL_ID` | Channel username or numeric ID | *required* |
| `WATCHLIST` | Comma-separated tickers (Yahoo Finance format) | `BTC-USD,ETH-USD,BNB-USD,SOL-USD,XRP-USD` |
| `SIGNAL_INTERVAL_MINUTES` | How often to scan (minutes) | `30` |
| `RSI_OVERSOLD` | RSI threshold for oversold (buy) | `30` |
| `RSI_OVERBOUGHT` | RSI threshold for overbought (sell) | `70` |
| `MIN_SIGNAL_STRENGTH` | Minimum composite strength to broadcast (0–1) | `0.6` |
| `HISTORY_PERIOD` | yfinance history period | `90d` |
| `CANDLE_INTERVAL` | yfinance candle interval | `1h` |

### 4 – Run

```bash
python main.py
```

---

## Signal Example

```
🟢 *BTC-USD*  —  BUY
💰 Price: `67432.1500`
📊 Strength: ████████░░ 80%

*Reasons:*
  • RSI oversold (28.4 < 30.0)
  • MACD bullish crossover
```

---

## Project Structure

```
Med/
├── main.py          # Bot entry-point + command handlers + scheduler
├── signals.py       # Market data fetching & technical-analysis engine
├── config.py        # Centralised configuration from environment variables
├── requirements.txt
├── .env.example     # Template – copy to .env and fill in values
└── tests/
    └── test_signals.py  # Unit tests (offline, no real network calls)
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Architecture

```
main.py
  └─ APScheduler (every N minutes)
        └─ signals.get_trending_signals()
              ├─ yfinance.download()      ← market data
              └─ pandas_ta (RSI/MACD/BB/EMA) ← indicators
                    └─ Signal objects → Telegram channel
```

