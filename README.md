# Med – Trending Signal Channel for Telegram

A Python Telegram bot that continuously monitors **US stock market** data and crypto,
generates **buy / sell signals** using technical analysis, and broadcasts them both to a
Telegram channel and as **direct messages to subscribed users**.

---

## Features

| Feature | Detail |
|---|---|
| **US stock market focus** | Default watchlist: AAPL, TSLA, MSFT, NVDA, AMZN, GOOGL, META, SPY + BTC/ETH |
| **Technical indicators** | RSI, MACD, Bollinger Bands, EMA crossover |
| **Signal strength scoring** | 0 – 100 % composite score per asset |
| **Automatic channel broadcast** | All qualifying signals posted to channel on schedule |
| **User subscriptions** | `/subscribe` to receive BUY alerts as personal DMs |
| **Bot commands** | `/start`, `/subscribe`, `/unsubscribe`, `/signals`, `/watchlist`, `/help` |
| **Customisable watchlist** | Any Yahoo Finance ticker via `.env` |

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
| `WATCHLIST` | Comma-separated tickers (Yahoo Finance format) | `AAPL,TSLA,MSFT,NVDA,AMZN,GOOGL,META,SPY,BTC-USD,ETH-USD` |
| `SIGNAL_INTERVAL_MINUTES` | How often to scan (minutes) | `30` |
| `RSI_OVERSOLD` | RSI threshold for oversold (buy) | `30` |
| `RSI_OVERBOUGHT` | RSI threshold for overbought (sell) | `70` |
| `MIN_SIGNAL_STRENGTH` | Minimum composite strength to broadcast (0–1) | `0.6` |
| `HISTORY_PERIOD` | yfinance history period | `90d` |
| `CANDLE_INTERVAL` | yfinance candle interval | `1h` |
| `SUBSCRIBERS_FILE` | Path to the subscriber list JSON file | `subscribers.json` |

### 4 – Run

```bash
python main.py
```

---

## How Subscriptions Work

1. A user opens the bot and sends `/subscribe`.
2. Their chat ID is saved to `subscribers.json`.
3. Every time the scheduler runs and finds a **BUY** signal, the bot sends a DM to every subscriber.
4. To stop receiving alerts the user sends `/unsubscribe`.

> **Note:** The bot must have been started by the user (i.e. the user messaged the bot at least once) before it can send them DMs.

---

## Signal Example

```
🟢 *AAPL*  —  BUY
💰 Price: `175.4800`
📊 Strength: ████████░░ 80%

*Reasons:*
  • RSI oversold (28.4 < 30.0)
  • MACD bullish crossover
```

---

## Project Structure

```
Med/
├── main.py           # Bot entry-point + command handlers + scheduler
├── signals.py        # Market data fetching & technical-analysis engine
├── subscribers.py    # JSON-backed subscriber store (/subscribe /unsubscribe)
├── config.py         # Centralised configuration from environment variables
├── requirements.txt
├── .env.example      # Template – copy to .env and fill in values
└── tests/
    ├── conftest.py          # Shared fake-config fixture
    ├── test_signals.py      # Signal engine unit tests (offline)
    ├── test_subscribers.py  # Subscriber store unit tests
    └── test_broadcast.py    # Broadcast + DM dispatch unit tests
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
              ├─ yfinance.download()           ← US stock + crypto market data
              └─ pandas_ta (RSI/MACD/BB/EMA)   ← indicators
                    └─ Signal objects
                          ├─ → Telegram channel  (all signals)
                          └─ → subscribed users  (BUY signals only, via DM)
```

