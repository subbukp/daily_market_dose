import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Bot
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


async def _send(message: str):
    """Send a message via Telegram bot (async)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
        )

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    # Telegram has a 4096 char limit per message — split if needed
    max_len = 4000
    if len(message) <= max_len:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown",
        )
    else:
        # Split into chunks at line boundaries
        chunks = []
        current = ""
        for line in message.split("\n"):
            if len(current) + len(line) + 1 > max_len:
                chunks.append(current)
                current = line + "\n"
            else:
                current += line + "\n"
        if current:
            chunks.append(current)

        for i, chunk in enumerate(chunks):
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=chunk.strip(),
                parse_mode="Markdown",
            )


def send_telegram(message: str):
    """Send a Telegram message (sync wrapper)."""
    asyncio.run(_send(message))


