"""
tests/test_broadcast.py – Unit tests for the broadcast_signals helper in main.py.

All Telegram API calls and signal fetching are mocked.
"""
from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from signals import Signal, SignalType
from subscribers import SubscriberStore


def _run(coro):
    return asyncio.run(coro)


class TestBroadcastSignals(unittest.TestCase):
    """Tests for broadcast_signals() in main.py."""

    def _make_app(self) -> MagicMock:
        app = MagicMock()
        app.bot.send_message = AsyncMock()
        return app

    def _patch_store(self, subscribers: list[int], tmp_path: Path):
        """Return a SubscriberStore loaded with given IDs."""
        import json
        tmp_path.write_text(json.dumps(subscribers))
        return SubscriberStore(path=tmp_path)

    def test_no_signals_sends_nothing(self):
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=".json"))
        store = self._patch_store([111], tmp)

        with patch("main.get_trending_signals", return_value=[]), \
             patch("main.subscriber_store", store):
            from main import broadcast_signals
            app = self._make_app()
            _run(broadcast_signals(app))
            app.bot.send_message.assert_not_called()

    def test_buy_signal_dmed_to_subscribers(self):
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=".json"))
        store = self._patch_store([111, 222], tmp)

        buy = Signal("AAPL", SignalType.BUY, 0.85, 175.0, ["RSI oversold"])

        with patch("main.get_trending_signals", return_value=[buy]), \
             patch("main.subscriber_store", store):
            from main import broadcast_signals
            app = self._make_app()
            _run(broadcast_signals(app))

        calls = app.bot.send_message.call_args_list
        dm_chats = {c.kwargs.get("chat_id") or c.args[0] for c in calls}
        self.assertIn(111, dm_chats)
        self.assertIn(222, dm_chats)

    def test_sell_signal_not_dmed_to_subscribers(self):
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=".json"))
        store = self._patch_store([111], tmp)

        sell = Signal("TSLA", SignalType.SELL, 0.80, 200.0, ["RSI overbought"])

        with patch("main.get_trending_signals", return_value=[sell]), \
             patch("main.subscriber_store", store):
            from main import broadcast_signals
            app = self._make_app()
            _run(broadcast_signals(app))

        calls = app.bot.send_message.call_args_list
        dm_chats = [c.kwargs.get("chat_id") or c.args[0] for c in calls]
        # 111 should NOT appear – only the channel should have been messaged
        self.assertNotIn(111, dm_chats)
        self.assertIn("@test_channel", dm_chats)

    def test_blocked_user_removed_from_store(self):
        import tempfile
        from telegram.error import Forbidden
        tmp = Path(tempfile.mktemp(suffix=".json"))
        store = self._patch_store([111], tmp)

        buy = Signal("AAPL", SignalType.BUY, 0.85, 175.0, ["RSI oversold"])

        async def send_message_raises(*args, **kwargs):
            if kwargs.get("chat_id") == 111 or (args and args[0] == 111):
                raise Forbidden("blocked")
            return MagicMock()

        with patch("main.get_trending_signals", return_value=[buy]), \
             patch("main.subscriber_store", store):
            from main import broadcast_signals
            app = self._make_app()
            app.bot.send_message.side_effect = send_message_raises
            _run(broadcast_signals(app))

        self.assertNotIn(111, store)


if __name__ == "__main__":
    unittest.main()
