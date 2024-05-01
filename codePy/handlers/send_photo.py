from codePy.telegram_bot.keyboard import get_keyboard
from codePy.telegram_bot.create_bot import bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram import types, Dispatcher
from aiogram.filters import Command
import os


async def photo_message(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        path = data.get('path_photo')
        print(path)
        if path is None:
            photo = FSInputFile(os.path.abspath('../input/image/default.png'))
        else:
            photo = FSInputFile(os.path.abspath(path))
    except KeyError:
        photo = FSInputFile(path=os.path.abspath('../input/image/default.png'))

    await bot.send_photo(message.chat.id, photo, reply_markup=get_keyboard(await state.get_state()))


def send_photo_in_telegram(dp: Dispatcher):
    dp.message.register(photo_message, Command(commands=['photo']))
