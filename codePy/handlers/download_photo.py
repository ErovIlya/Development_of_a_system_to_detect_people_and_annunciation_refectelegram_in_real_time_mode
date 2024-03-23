from codePy.telegram_bot.create_bot import TOKEN_API, bot
from codePy.yolo_model.found_people_on_photo import found_people_on_photo
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.types import ContentType
from PIL import Image
import datetime
import requests
import io
import os


URI_INFO = f"https://api.telegram.org/bot{TOKEN_API}/getFile?file_id="
URI = f"https://api.telegram.org/file/bot{TOKEN_API}/"


async def download_photo_from_bot(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.PHOTO:
        # await bot.send_message(chat_id=message.chat.id, text="Файл получен")
        await message.reply(text="Файл получен")
        file_id = message.photo[-1].file_id
        resp = requests.get(URI_INFO + file_id)
        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)

        img = Image.open(io.BytesIO(img.content))
        now_date = datetime.datetime.now().strftime('%d-%m-%Y')
        now_time = datetime.datetime.now().strftime('%H-%M-%S')

        if not os.path.exists('../download'):
            os.mkdir('../download')
        if not os.path.exists(f'../download/{now_date}'):
            os.mkdir(f'../download/{now_date}')

        # img_path = os.path.abspath(rf'../../download/{now_date}/{now_time}.png')

        img_path = f'../download/{now_date}/{now_time}.png'
        img.save(img_path, format='PNG')
        print(img_path)

        await message.reply(text=f'Файл сохранён: {img_path}')
        # await bot.send_message(chat_id=message.chat.id, text=f'Файл сохранён: {img_path})

        result_str, result_path = found_people_on_photo(img_path, now_date, now_time)

        data = {'path': result_path}
        await state.set_data(data)
        test_data = await state.get_data()
        print(test_data['path'])
        await bot.send_message(chat_id=message.chat.id, text=result_str)
    else:
        await message.reply(text='Фотография не обнаружена')


def download_photo_telegram(dp: Dispatcher):
    dp.message.register(download_photo_from_bot, F.photo)
    # dp.register_message_handler(download_photo_from_bot, content_types=ContentType.PHOTO)
