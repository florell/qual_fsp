import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from check_db import get_metrics

# TOKEN = getenv("BOT_TOKEN")
TOKEN = '6391602835:AAGpy8b_WbygrfBYGk7x9m8VUHc84_znk6o'

dp = Dispatcher()

user_messages = {}

class DBInfo(StatesGroup):
    database = State()
    user = State()
    password = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    kb = [
            [types.KeyboardButton(text='change db')],
           ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer(f"hello", reply_markup=keyboard)


@dp.message(F.text.lower() == "change db")
async def get_info(message: types.Message, state: FSMContext):
    global semaphore
    semaphore.set()
    user_id = message.chat.id
    await delete_user_message(message.bot, message)
    await state.set_state(DBInfo.database)
    await message.answer('Введите название базы данных')


@dp.message(DBInfo.database)
async def state1(message: Message, state: FSMContext):
    await state.update_data(database=message.text)
    await state.set_state(DBInfo.user)

    await message.answer('Введите имя пользователя')


@dp.message(DBInfo.user)
async def state2(message: Message, state: FSMContext):
    await state.update_data(user=message.text)
    await state.set_state(DBInfo.password)

    await message.answer('Введите пароль')
    

@dp.message(DBInfo.password)
async def state3(message: Message, state: FSMContext):
    data = await state.update_data(password=message.text)
    await state.set_state(DBInfo.user)
    await send_result(message=message, data=data)


async def send_result(message: Message, data: Dict[str, Any]):
    metrics = get_metrics(database=data['database'],
                          user=data['user'],
                          password=data['password'])

    message = await message.reply(pretty_print(metrics))
    user_messages[message.chat.id] = {'message_id': message.message_id,
                                      'data': data
                                      }


def pretty_print(metrics):
    if metrics['type'] == 'error':
        return metrics['data']['error']

    return f'''Количество активных подключений: {metrics['data']['connections']}
Количество значений LWLock: {metrics['data']['LWLock'] if metrics['data']['LWLock'] else 0}
Свободное место на диске (в байтах): {metrics['data']['disk_space']}
Загруженность процессора (%): {metrics['data']['cpu']}
    '''


async def send_metrics_to_users(bot: Bot, user_id: int) -> None:
    if user_id in user_messages:
        message_id = user_messages[user_id]['message_id']
        data = user_messages[user_id]['data']
        metrics = get_metrics(database=data['database'],
                              user=data['user'],
                              password=data['password'])
        if metrics['type'] != 'error':
            await bot.edit_message_text(chat_id=user_id, message_id=message_id, 
                                        text=pretty_print(metrics), parse_mode=ParseMode.HTML)
    # else:
    #     message = await bot.send_message(chat_id=user_id, text='Выберете change db', parse_mode=ParseMode.HTML)
        # user_messages[user_id] = {'message_id': message.message_id,
        #                                   'data': None
        #                           }


async def delete_user_message(bot: Bot, message: Message) -> None:
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def scheduled_get_info(bot: Bot, semaphore: asyncio.Event) -> None:
     while True:
         await semaphore.wait()

         for user_id in user_messages.keys():
             await send_metrics_to_users(bot, user_id)
         await asyncio.sleep(15)


async def main() -> None:
    global semaphore
    semaphore = asyncio.Event()

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    asyncio.create_task(scheduled_get_info(bot, semaphore))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())