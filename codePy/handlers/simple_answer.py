from codePy.telegram_bot.keyboard import keyboard_start, get_keyboard
from codePy.telegram_bot.create_bot import bot
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher
from aiogram.filters import Command


hello = """
/hi - приветствие;
/info - краткая информация о боте;
/system - краткая информация о системе:
/photo - результат предыдущего поиска людей на фотографии;
При отпавке фото будет произведён поиск людей;
/start - начало работы видеокамеры;
/stop - конец работы видеокамеры.
"""


async def send_message_error_in_stop(chat_id, text_message):
    await bot.send_message(chat_id, text_message, reply_markup=keyboard_start)


async def send_message_stop_complete(chat_id, text_message):
    await bot.send_message(chat_id, text_message, reply_markup=keyboard_start)


async def hi_message(message: types.Message, state):
    await message.answer(f"Привет, {message.from_user.full_name}",
                         reply_markup=get_keyboard(await state.get_state()))


async def info_message(message: types.Message, state: FSMContext):
    await message.answer(hello, reply_markup=get_keyboard(await state.get_state()))


def hello_send_in_telegram(dp: Dispatcher):
    dp.message.register(hi_message, Command(commands=['hi']))
    dp.message.register(info_message, Command(commands=['info']))
