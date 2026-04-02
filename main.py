"""
main.py – Entry point for the Med Trending Signal Telegram Bot.

Features
--------
* Periodic scanning of the watchlist for trending buy/sell signals.
* Automatic broadcast of qualifying signals to the configured Telegram channel.
* Bot commands for manual interaction:
    /start    – welcome message
    /signals  – trigger an immediate scan and display results
    /watchlist – show the current watchlist
    /help     – list available commands
"""
from __future__ import annotations

import logging
import textwrap
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import config
from signals import SignalType, get_trending_signals

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Scheduler (module-level so it survives across calls) ─────────────────────
scheduler = AsyncIOScheduler(timezone="UTC")


# ── Helper: broadcast signals to channel ─────────────────────────────────────

async def broadcast_signals(app: Application) -> None:
    """Fetch trending signals and post each one to the channel."""
    logger.info("Running scheduled signal scan…")
    signals = get_trending_signals()

    if not signals:
        logger.info("No qualifying signals found.")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = f"📡 *Trending Signals*  —  {timestamp}\n{'─' * 32}"

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

    logger.info("Broadcasted %d signal(s) to %s.", len(signals), config.TELEGRAM_CHANNEL_ID)


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = textwrap.dedent(
        f"""
        👋 *Welcome to the Med Trending Signal Bot!*

        I monitor {len(config.WATCHLIST)} asset(s) and post trading signals to the channel.

        Use /help to see available commands.
        """
    ).strip()
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = textwrap.dedent(
        """
        *Available commands*

        /start      – Welcome message
        /signals    – Run an immediate signal scan
        /watchlist  – Show monitored tickers
        /help       – This help message
        """
    ).strip()
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


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
    app.add_handler(CommandHandler("watchlist", cmd_watchlist))
    app.add_handler(CommandHandler("signals", cmd_signals))

    logger.info("Bot is starting…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
