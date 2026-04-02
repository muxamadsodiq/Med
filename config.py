"""
config.py – centralised configuration loaded from environment variables / .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{key}' is not set. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


def _float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = _required("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID: str = _required("TELEGRAM_CHANNEL_ID")

# ── Watchlist ─────────────────────────────────────────────────────────────────
# Defaults include major US stocks and leading crypto pairs so the bot monitors
# both markets out of the box.  Override via the WATCHLIST env var.
_DEFAULT_WATCHLIST = (
    # US stocks
    "AAPL,TSLA,MSFT,NVDA,AMZN,GOOGL,META,SPY,"
    # Crypto
    "BTC-USD,ETH-USD"
)
_raw_watchlist = os.getenv("WATCHLIST", _DEFAULT_WATCHLIST)
WATCHLIST: list[str] = [t.strip() for t in _raw_watchlist.split(",") if t.strip()]

# ── Scheduler ─────────────────────────────────────────────────────────────────
SIGNAL_INTERVAL_MINUTES: int = _int("SIGNAL_INTERVAL_MINUTES", 30)

# ── Signal thresholds ─────────────────────────────────────────────────────────
RSI_OVERSOLD: float = _float("RSI_OVERSOLD", 30)
RSI_OVERBOUGHT: float = _float("RSI_OVERBOUGHT", 70)
MIN_SIGNAL_STRENGTH: float = _float("MIN_SIGNAL_STRENGTH", 0.6)

# ── Data fetch ────────────────────────────────────────────────────────────────
# How many daily candles to download for indicator calculations
HISTORY_PERIOD: str = os.getenv("HISTORY_PERIOD", "90d")
CANDLE_INTERVAL: str = os.getenv("CANDLE_INTERVAL", "1h")
