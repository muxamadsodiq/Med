"""
main.py – Entry point for the Med Trending Signal Telegram Bot.

Features
--------
* Monitors US stocks (AAPL, TSLA, MSFT, NVDA …) and crypto by default.
* Periodic scanning of the watchlist for trending buy/sell signals.
* Automatic broadcast of qualifying signals to the configured Telegram channel.
* BUY signals are also sent as direct messages to every subscribed user.
* Bot commands for manual interaction:
    /start       – welcome message + subscription prompt
    /subscribe   – subscribe to receive BUY signal DMs
    /unsubscribe – stop receiving DMs
    /signals     – trigger an immediate scan and display results
    /watchlist   – show the current watchlist
    /help        – list available commands
"""
from __future__ import annotations

import logging
import textwrap
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import config
from signals import SignalType, get_trending_signals
from subscribers import store as subscriber_store

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Scheduler (module-level so it survives across calls) ─────────────────────
scheduler = AsyncIOScheduler(timezone="UTC")


# ── Helper: broadcast signals to channel + DM subscribers ────────────────────

async def broadcast_signals(app: Application) -> None:
    """Fetch trending signals, post to the channel, and DM subscribed users."""
    logger.info("Running scheduled signal scan…")
    signals = get_trending_signals()

    if not signals:
        logger.info("No qualifying signals found.")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = f"📡 *Trending Signals*  —  {timestamp}\n{'─' * 32}"

    # ── Channel broadcast (all signals) ──────────────────────────────────────
    await app.bot.send_message(
        chat_id=config.TELEGRAM_CHANNEL_ID,
        text=header,
        parse_mode=ParseMode.MARKDOWN,
    )
    for signal in signals:
        await app.bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=signal.to_message(),
            parse_mode=ParseMode.MARKDOWN,
        )
    logger.info("Broadcasted %d signal(s) to channel %s.", len(signals), config.TELEGRAM_CHANNEL_ID)

    # ── DM subscribed users (BUY signals only) ────────────────────────────────
    buy_signals = [s for s in signals if s.signal_type == SignalType.BUY]
    if not buy_signals:
        return

    subscribers = subscriber_store.all()
    if not subscribers:
        return

    dm_header = f"🔔 *New BUY Signal Alert*  —  {timestamp}\n{'─' * 32}"
    stale_ids: list[int] = []

    for chat_id in subscribers:
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=dm_header,
                parse_mode=ParseMode.MARKDOWN,
            )
            for signal in buy_signals:
                await app.bot.send_message(
                    chat_id=chat_id,
                    text=signal.to_message(),
                    parse_mode=ParseMode.MARKDOWN,
                )
        except Forbidden:
            # User blocked the bot – remove from subscriber list
            logger.info("User %s blocked the bot; removing from subscribers.", chat_id)
            stale_ids.append(chat_id)
        except TelegramError as exc:
            logger.warning("Could not DM %s: %s", chat_id, exc)

    for chat_id in stale_ids:
        subscriber_store.remove(chat_id)

    logger.info(
        "Sent %d BUY signal(s) to %d subscriber(s).",
        len(buy_signals),
        len(subscribers) - len(stale_ids),
    )


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = textwrap.dedent(
        f"""
        👋 *Welcome to the Med Trending Signal Bot\\!*

        I continuously monitor *US stock market* and crypto assets for trading signals\\.

        📈 Monitored assets: {len(config.WATCHLIST)} tickers
        🔔 Want BUY alerts in your DMs? Use /subscribe

        Use /help to see all available commands\\.
        """
    ).strip()
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = textwrap.dedent(
        """
        *Available commands*

        /subscribe    – Get BUY signal alerts via DM
        /unsubscribe  – Stop receiving DM alerts
        /signals      – Run an immediate signal scan
        /watchlist    – Show monitored tickers
        /start        – Welcome message
        /help         – This help message
        """
    ).strip()
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if subscriber_store.add(chat_id):
        await update.message.reply_text(
            "✅ You're subscribed\\!  You'll receive BUY signal alerts as direct messages\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.info("New subscriber: %s", chat_id)
    else:
        await update.message.reply_text(
            "ℹ️ You are already subscribed\\.  Use /unsubscribe to stop receiving alerts\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def cmd_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if subscriber_store.remove(chat_id):
        await update.message.reply_text(
            "👋 You have been unsubscribed\\.  Use /subscribe any time to re-enable alerts\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.info("Unsubscribed: %s", chat_id)
    else:
        await update.message.reply_text(
            "ℹ️ You are not currently subscribed\\.  Use /subscribe to start receiving alerts\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def cmd_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = "\n".join(f"  • `{t}`" for t in config.WATCHLIST)
    text = f"*Current watchlist ({len(config.WATCHLIST)} tickers):*\n{items}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_signals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🔍 Scanning for signals, please wait…")

    signals = get_trending_signals()

    if not signals:
        await update.message.reply_text(
            "✅ Scan complete.  No qualifying signals found right now."
        )
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = f"📡 *Scan results*  —  {timestamp}\n{'─' * 32}"
    await update.message.reply_text(header, parse_mode=ParseMode.MARKDOWN)

    for signal in signals:
        await update.message.reply_text(
            signal.to_message(),
            parse_mode=ParseMode.MARKDOWN,
        )


# ── Bot lifecycle ─────────────────────────────────────────────────────────────

async def on_startup(app: Application) -> None:
    """Called once after the bot is initialised – start the scheduler."""
    scheduler.add_job(
        broadcast_signals,
        trigger="interval",
        minutes=config.SIGNAL_INTERVAL_MINUTES,
        args=[app],
        id="signal_broadcast",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started – broadcasting signals every %d minute(s).",
        config.SIGNAL_INTERVAL_MINUTES,
    )


async def on_shutdown(app: Application) -> None:
    """Called when the bot shuts down."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")


def main() -> None:
    app = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("subscribe", cmd_subscribe))
    app.add_handler(CommandHandler("unsubscribe", cmd_unsubscribe))
    app.add_handler(CommandHandler("watchlist", cmd_watchlist))
    app.add_handler(CommandHandler("signals", cmd_signals))

    logger.info("Bot is starting…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

