import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from check_db import get_metrics

# TOKEN = getenv("BOT_TOKEN")
TOKEN = '6391602835:AAGCm1sqptuxQxNXL9BhrCUJSPDuw9qMBfc'

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    kb = [
            [types.KeyboardButton(text='get info')],
           ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer(f"hello", reply_markup=keyboard)


@dp.message(F.text.lower() == "get info")
async def with_puree(message: types.Message):
    metrics = get_metrics()
    await message.reply(metrics)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
