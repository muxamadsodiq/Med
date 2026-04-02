"""
tests/conftest.py – Shared pytest configuration.

Sets up a complete fake `config` module before any test file is imported, so
all modules that do `import config` get consistent stub values without needing
real environment variables.
"""
from __future__ import annotations

import sys
import types

_fake_config = types.ModuleType("config")

# Telegram
_fake_config.TELEGRAM_BOT_TOKEN = "fake:token"
_fake_config.TELEGRAM_CHANNEL_ID = "@test_channel"

# Watchlist
_fake_config.WATCHLIST = ["AAPL", "BTC-USD"]

# Scheduler
_fake_config.SIGNAL_INTERVAL_MINUTES = 30

# Signal thresholds
_fake_config.RSI_OVERSOLD = 30.0
_fake_config.RSI_OVERBOUGHT = 70.0
_fake_config.MIN_SIGNAL_STRENGTH = 0.6

# Data fetch
_fake_config.HISTORY_PERIOD = "90d"
_fake_config.CANDLE_INTERVAL = "1h"

# Install before any test module imports `config`
sys.modules["config"] = _fake_config
