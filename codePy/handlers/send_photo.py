from codePy.telegram_bot.create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.types import InputFile


async def photo_message(message: types.Message, state: FSMContext):
    # print(current_state)
    try:
        async with state.proxy() as data:
            path = data['path']
            print(path)
            photo = InputFile(data['path'])
    except KeyError:
        photo = InputFile("input/image/default.png")

    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    await message.delete()


def send_photo_in_telegram(dp: Dispatcher):
    dp.register_message_handler(photo_message, commands=['photo'])
