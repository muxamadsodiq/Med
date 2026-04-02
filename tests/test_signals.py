"""
tests/test_signals.py – Unit tests for the signal generation module.

All tests are fully offline: no real network calls are made.
yfinance.download is patched with synthetic OHLCV DataFrames.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from signals import Signal, SignalType, _analyse, _fetch_ohlcv, get_trending_signals


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 100,
    trend: str = "up",
    oversold: bool = False,
    overbought: bool = False,
) -> pd.DataFrame:
    """Build a synthetic OHLCV DataFrame."""
    rng = np.random.default_rng(seed=42)

    if trend == "up":
        close = np.linspace(100, 200, n) + rng.normal(0, 1, n)
    elif trend == "down":
        close = np.linspace(200, 100, n) + rng.normal(0, 1, n)
    else:
        close = np.full(n, 150.0) + rng.normal(0, 0.5, n)

    if oversold:
        # Force very low recent prices so RSI drops below 30
        close[-5:] = close[-5:] * 0.50

    if overbought:
        # Force very high recent prices so RSI pushes above 70
        close[-5:] = close[-5:] * 2.0

    idx = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {
            "open": close * 0.99,
            "high": close * 1.01,
            "low": close * 0.98,
            "close": close,
            "volume": rng.integers(1_000, 10_000, n).astype(float),
        },
        index=idx,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestSignalModel(unittest.TestCase):
    def test_buy_emoji(self):
        s = Signal("BTC-USD", SignalType.BUY, 0.8, 50_000.0, ["RSI oversold"])
        self.assertEqual(s.emoji(), "🟢")

    def test_sell_emoji(self):
        s = Signal("ETH-USD", SignalType.SELL, 0.75, 3_000.0, ["RSI overbought"])
        self.assertEqual(s.emoji(), "🔴")

    def test_neutral_emoji(self):
        s = Signal("BNB-USD", SignalType.NEUTRAL, 0.0, 400.0)
        self.assertEqual(s.emoji(), "⚪")

    def test_strength_bar_full(self):
        s = Signal("BTC-USD", SignalType.BUY, 1.0, 50_000.0)
        self.assertEqual(s.strength_bar(10), "█" * 10)

    def test_strength_bar_empty(self):
        s = Signal("BTC-USD", SignalType.NEUTRAL, 0.0, 50_000.0)
        self.assertEqual(s.strength_bar(10), "░" * 10)

    def test_to_message_contains_ticker(self):
        s = Signal("BTC-USD", SignalType.BUY, 0.8, 50_000.0, ["RSI oversold"])
        msg = s.to_message()
        self.assertIn("BTC-USD", msg)
        self.assertIn("BUY", msg)
        self.assertIn("RSI oversold", msg)


class TestAnalyse(unittest.TestCase):
    def test_returns_tuple(self):
        df = _make_df()
        signal_type, strength, reasons = _analyse(df)
        self.assertIsInstance(signal_type, SignalType)
        self.assertIsInstance(strength, float)
        self.assertIsInstance(reasons, list)

    def test_strength_between_0_and_1(self):
        for trend in ("up", "down", "flat"):
            df = _make_df(trend=trend)
            _, strength, _ = _analyse(df)
            self.assertGreaterEqual(strength, 0.0)
            self.assertLessEqual(strength, 1.0)

    def test_oversold_produces_buy_reason(self):
        df = _make_df(oversold=True)
        signal_type, strength, reasons = _analyse(df)
        rsi_reasons = [r for r in reasons if "oversold" in r.lower()]
        # At least one RSI-oversold reason should appear
        self.assertTrue(len(rsi_reasons) > 0, f"Expected RSI-oversold reason, got: {reasons}")

    def test_overbought_produces_sell_reason(self):
        df = _make_df(overbought=True)
        signal_type, strength, reasons = _analyse(df)
        rsi_reasons = [r for r in reasons if "overbought" in r.lower()]
        self.assertTrue(len(rsi_reasons) > 0, f"Expected RSI-overbought reason, got: {reasons}")


class TestFetchOHLCV(unittest.TestCase):
    @patch("signals.yf.download")
    def test_returns_none_on_empty_df(self, mock_dl):
        mock_dl.return_value = pd.DataFrame()
        result = _fetch_ohlcv("FAKE-USD")
        self.assertIsNone(result)

    @patch("signals.yf.download")
    def test_returns_none_on_exception(self, mock_dl):
        mock_dl.side_effect = Exception("network error")
        result = _fetch_ohlcv("FAKE-USD")
        self.assertIsNone(result)

    @patch("signals.yf.download")
    def test_returns_dataframe_on_success(self, mock_dl):
        mock_dl.return_value = _make_df()
        result = _fetch_ohlcv("BTC-USD")
        self.assertIsNotNone(result)
        self.assertIn("close", result.columns)


class TestGetTrendingSignals(unittest.TestCase):
    @patch("signals.analyse_ticker")
    def test_filters_by_min_strength(self, mock_analyse):
        # One strong BUY signal, one weak one, one NEUTRAL
        mock_analyse.side_effect = [
            Signal("BTC-USD", SignalType.BUY, 0.9, 50_000.0, ["RSI oversold"]),
            Signal("ETH-USD", SignalType.BUY, 0.3, 3_000.0, ["RSI oversold"]),
        ]
        signals = get_trending_signals(["BTC-USD", "ETH-USD"])
        # Only the strong one should survive the MIN_SIGNAL_STRENGTH=0.6 filter
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].ticker, "BTC-USD")

    @patch("signals.analyse_ticker")
    def test_sorted_by_strength_descending(self, mock_analyse):
        mock_analyse.side_effect = [
            Signal("ETH-USD", SignalType.SELL, 0.7, 3_000.0, ["MACD crossover"]),
            Signal("BTC-USD", SignalType.BUY, 0.9, 50_000.0, ["RSI oversold"]),
        ]
        signals = get_trending_signals(["ETH-USD", "BTC-USD"])
        self.assertEqual(signals[0].ticker, "BTC-USD")
        self.assertEqual(signals[1].ticker, "ETH-USD")

    @patch("signals.analyse_ticker")
    def test_neutral_signals_excluded(self, mock_analyse):
        mock_analyse.return_value = Signal("BTC-USD", SignalType.NEUTRAL, 0.0, 50_000.0)
        signals = get_trending_signals(["BTC-USD"])
        self.assertEqual(signals, [])

    @patch("signals.analyse_ticker")
    def test_none_ticker_skipped(self, mock_analyse):
        mock_analyse.return_value = None
        signals = get_trending_signals(["BAD-USD"])
        self.assertEqual(signals, [])


if __name__ == "__main__":
    unittest.main()
