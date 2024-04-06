from codePy.telegram_bot.create_bot import bot
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


async def send_message_for_interim_step(chat_id, text_message):
    await bot.send_message(chat_id, text_message)


async def hi_message(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}")


async def info_message(message: types.Message):
    await message.answer(hello)


def hello_send_in_telegram(dp: Dispatcher):
    dp.message.register(hi_message, Command(commands=['hi']))
    dp.message.register(info_message, Command(commands=['info']))
