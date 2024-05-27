#!/usr/bin/env python
"""Telegram Bot to interact with FastAPI backend."""

import asyncio
import contextlib
from dotenv import load_dotenv
import logging
from typing import NoReturn
import requests
from telegram import Bot, Update
from telegram.error import Forbidden, NetworkError
import os

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FASTAPI_BASE_URL = "http://localhost:8000"

async def main() -> NoReturn:
    """Run the bot."""
    async with Bot(TELEGRAM_BOT_TOKEN) as bot:
        try:
            update_id = (await bot.get_updates())[0].update_id
        except IndexError:
            update_id = None

        logger.info("Listening for new messages...")
        while True:
            try:
                update_id = await echo(bot, update_id)
            except NetworkError:
                await asyncio.sleep(1)
            except Forbidden:
                # The user has removed or blocked the bot.
                update_id += 1

async def echo(bot: Bot, update_id: int) -> int:
    """Echo the message the user sent."""
    updates = await bot.get_updates(offset=update_id, timeout=10, allowed_updates=Update.ALL_TYPES)
    print('updates', updates)
    for update in updates:
        next_update_id = update.update_id + 1

        if update.message and update.message.text:
            logger.info("Found message %s!", update.message.text)
            
            user_input = update.message.text
            chat_id = update.message.chat_id

            # Check if there's a session ID in the user's context data
            session_id = '123'  # Placeholder for session ID management
            print('user_input', user_input)
            # Send the message to the FastAPI server
            response = requests.post(
                f"{FASTAPI_BASE_URL}/chat",
                json={"session_id": session_id, "input": user_input},
                headers={
                    'Content-Type': 'application/json'
                }
            )
            response_data = response.json()

            print(response_data)

            # Save the session ID in the user's context data
            # session_id = response_data['session_id']

            # Reply with the assistant's response
            await update.message.reply_text(response_data['response'])

        return next_update_id
    return update_id

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):  # Ignore exception when Ctrl-C is pressed
        asyncio.run(main())
