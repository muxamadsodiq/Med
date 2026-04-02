"""
signals.py – Market data fetching and technical-analysis-based signal generation.

Supported indicators
--------------------
* RSI  – overbought / oversold
* MACD – bullish / bearish crossover
* Bollinger Bands – price touching lower / upper band
* EMA trend – short EMA vs long EMA cross

Each indicator contributes a partial score.  The combined score (0.0 – 1.0)
determines signal strength.  Signals with strength ≥ config.MIN_SIGNAL_STRENGTH
are considered worth broadcasting.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import pandas as pd
import pandas_ta as ta
import yfinance as yf

import config

logger = logging.getLogger(__name__)


# ── Types ─────────────────────────────────────────────────────────────────────

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


@dataclass
class Signal:
    ticker: str
    signal_type: SignalType
    strength: float          # 0.0 – 1.0
    price: float
    reasons: list[str] = field(default_factory=list)

    # ── Formatting helpers ────────────────────────────────────────────────────

    def emoji(self) -> str:
        return {"BUY": "🟢", "SELL": "🔴", "NEUTRAL": "⚪"}.get(self.signal_type, "⚪")

    def strength_bar(self, width: int = 10) -> str:
        filled = round(self.strength * width)
        return "█" * filled + "░" * (width - filled)

    def to_message(self) -> str:
        lines = [
            f"{self.emoji()} *{self.ticker}*  —  {self.signal_type}",
            f"💰 Price: `{self.price:.4f}`",
            f"📊 Strength: {self.strength_bar()} {self.strength * 100:.0f}%",
            "",
            "*Reasons:*",
        ]
        for reason in self.reasons:
            lines.append(f"  • {reason}")
        return "\n".join(lines)


# ── Core analysis ─────────────────────────────────────────────────────────────

def _fetch_ohlcv(ticker: str) -> Optional[pd.DataFrame]:
    """Download OHLCV data from Yahoo Finance.  Returns None on failure."""
    try:
        df = yf.download(
            ticker,
            period=config.HISTORY_PERIOD,
            interval=config.CANDLE_INTERVAL,
            progress=False,
            auto_adjust=True,
        )
        if df is None or df.empty:
            logger.warning("No data returned for %s", ticker)
            return None
        # yfinance may return MultiIndex columns – flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.rename(columns=str.lower)
        return df
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch data for %s: %s", ticker, exc)
        return None


def _analyse(df: pd.DataFrame) -> tuple[SignalType, float, list[str]]:
    """Run indicators and return (signal_type, strength, reasons)."""
    buy_score = 0.0
    sell_score = 0.0
    reasons: list[str] = []

    close = df["close"]

    # ── RSI ───────────────────────────────────────────────────────────────────
    rsi_series = ta.rsi(close, length=14)
    if rsi_series is not None and not rsi_series.empty:
        rsi = float(rsi_series.iloc[-1])
        if rsi < config.RSI_OVERSOLD:
            buy_score += 0.3
            reasons.append(f"RSI oversold ({rsi:.1f} < {config.RSI_OVERSOLD})")
        elif rsi > config.RSI_OVERBOUGHT:
            sell_score += 0.3
            reasons.append(f"RSI overbought ({rsi:.1f} > {config.RSI_OVERBOUGHT})")

    # ── MACD ──────────────────────────────────────────────────────────────────
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    if macd_df is not None and not macd_df.empty:
        macd_col = [c for c in macd_df.columns if c.startswith("MACD_")
                    and "s" not in c.lower() and "h" not in c.lower()]
        signal_col = [c for c in macd_df.columns if "MACDs" in c]
        if macd_col and signal_col:
            macd_val = float(macd_df[macd_col[0]].iloc[-1])
            sig_val = float(macd_df[signal_col[0]].iloc[-1])
            prev_macd = float(macd_df[macd_col[0]].iloc[-2]) if len(macd_df) > 1 else macd_val
            prev_sig = float(macd_df[signal_col[0]].iloc[-2]) if len(macd_df) > 1 else sig_val

            if prev_macd <= prev_sig and macd_val > sig_val:
                buy_score += 0.35
                reasons.append("MACD bullish crossover")
            elif prev_macd >= prev_sig and macd_val < sig_val:
                sell_score += 0.35
                reasons.append("MACD bearish crossover")

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    bb_df = ta.bbands(close, length=20, std=2)
    if bb_df is not None and not bb_df.empty:
        lower_col = [c for c in bb_df.columns if "BBL" in c]
        upper_col = [c for c in bb_df.columns if "BBU" in c]
        if lower_col and upper_col:
            price = float(close.iloc[-1])
            lower = float(bb_df[lower_col[0]].iloc[-1])
            upper = float(bb_df[upper_col[0]].iloc[-1])
            if price <= lower:
                buy_score += 0.2
                reasons.append(f"Price at/below lower Bollinger Band ({price:.4f} ≤ {lower:.4f})")
            elif price >= upper:
                sell_score += 0.2
                reasons.append(f"Price at/above upper Bollinger Band ({price:.4f} ≥ {upper:.4f})")

    # ── EMA cross ─────────────────────────────────────────────────────────────
    ema_short = ta.ema(close, length=9)
    ema_long = ta.ema(close, length=21)
    if ema_short is not None and ema_long is not None:
        if not ema_short.empty and not ema_long.empty and len(ema_short) > 1:
            es_cur = float(ema_short.iloc[-1])
            el_cur = float(ema_long.iloc[-1])
            es_prev = float(ema_short.iloc[-2])
            el_prev = float(ema_long.iloc[-2])

            if es_prev <= el_prev and es_cur > el_cur:
                buy_score += 0.15
                reasons.append("EMA9 crossed above EMA21 (golden cross)")
            elif es_prev >= el_prev and es_cur < el_cur:
                sell_score += 0.15
                reasons.append("EMA9 crossed below EMA21 (death cross)")

    # ── Determine direction ───────────────────────────────────────────────────
    max_possible = 1.0   # scores are already normalised to sum ≤ 1.0

    if buy_score > sell_score:
        signal_type = SignalType.BUY
        strength = min(buy_score / max_possible, 1.0)
    elif sell_score > buy_score:
        signal_type = SignalType.SELL
        strength = min(sell_score / max_possible, 1.0)
    else:
        signal_type = SignalType.NEUTRAL
        strength = 0.0

    return signal_type, strength, reasons


def analyse_ticker(ticker: str) -> Optional[Signal]:
    """Fetch data and return a Signal for *ticker*, or None on failure."""
    df = _fetch_ohlcv(ticker)
    if df is None or len(df) < 30:
        return None

    signal_type, strength, reasons = _analyse(df)
    price = float(df["close"].iloc[-1])

    return Signal(
        ticker=ticker,
        signal_type=signal_type,
        strength=strength,
        price=price,
        reasons=reasons,
    )


def get_trending_signals(watchlist: list[str] | None = None) -> list[Signal]:
    """
    Analyse every ticker in *watchlist* (defaults to config.WATCHLIST) and
    return signals whose strength meets config.MIN_SIGNAL_STRENGTH.
    Results are sorted by strength descending.
    """
    watchlist = watchlist or config.WATCHLIST
    results: list[Signal] = []

    for ticker in watchlist:
        signal = analyse_ticker(ticker)
        if signal is None:
            continue
        if signal.signal_type != SignalType.NEUTRAL and signal.strength >= config.MIN_SIGNAL_STRENGTH:
            results.append(signal)
            logger.info(
                "Signal for %s: %s (strength=%.2f)",
                ticker,
                signal.signal_type,
                signal.strength,
            )

    results.sort(key=lambda s: s.strength, reverse=True)
    return results
