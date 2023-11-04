import asyncio
import logging
import sys

from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from check_db import get_metrics

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

user_messages = {}

async def send_metrics_to_users(bot: Bot, user_id: int, metrics: str) -> None:
    if user_id in user_messages:
        message_id = user_messages[user_id]
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=metrics, parse_mode=ParseMode.HTML)
    else:
        message = await bot.send_message(chat_id=user_id, text=metrics, parse_mode=ParseMode.HTML)
        user_messages[user_id] = message.message_id

async def delete_user_message(bot: Bot, message: Message) -> None:
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

async def scheduled_get_info(bot: Bot, semaphore: asyncio.Event) -> None:
    while True:
        await semaphore.wait()
        metrics = get_metrics()
        for user_id in user_messages.keys():
            await send_metrics_to_users(bot, user_id, metrics)
        await asyncio.sleep(15)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    user_id = message.chat.id
    kb = [
            [types.KeyboardButton(text='get info')],
           ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer(f"Hello", reply_markup=keyboard)

@dp.message(F.text.lower() == "get info")
async def with_puree(message: types.Message):
    global semaphore
    semaphore.set()
    user_id = message.chat.id
    await delete_user_message(message.bot, message)
    await send_metrics_to_users(message.bot, user_id, "Updating...")

async def main() -> None:
    global semaphore
    semaphore = asyncio.Event()
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    asyncio.create_task(scheduled_get_info(bot, semaphore))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
