from codePy.yolo_model.found_people_on_photo import found_people_on_photo
from codePy.utils.create_path_for_files import create_path_for_download_photo
from codePy.utils.create_path_for_files import get_abs_path
from codePy.utils.loggind_file import log_info, log_error
from codePy.telegram_bot.create_bot import TOKEN_API, bot
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
import codePy.utils.database as db
from PIL import Image
import requests
import io


URI_INFO = f"https://api.telegram.org/bot{TOKEN_API}/getFile?file_id="
URI = f"https://api.telegram.org/file/bot{TOKEN_API}/"


async def download_photo_from_bot(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Скачивание фотографии, отправленной боту
    """
    try:
        log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) отправил фотографию")
        await message.reply(text="Файл получен")

        file_id = message.photo[-1].file_id
        resp = requests.get(URI_INFO + file_id)
        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)

        img = Image.open(io.BytesIO(img.content))

        img_path = create_path_for_download_photo()
        img.save(img_path, format='PNG')
        log_info(f"Скачан и сохранён файл '{img_path}'")

        await message.reply(text=f'Файл сохранён: {img_path}')

        result_str, result_path = found_people_on_photo(img_path)

        db.insert_photo(message.chat.id, result_path)

        await bot.send_message(
            chat_id=message.chat.id,
            text=result_str
        )
    except Exception as e:
        log_error(e)


async def photo_message(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/photo]: Отправка последнего фото с обнаруженными на ней людьми
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/photo'")

    path = db.get_photo_path(message.chat.id)
    photo = FSInputFile(get_abs_path(path))

    log_info(f"Пользователю {message.from_user.full_name} (ID = {message.chat.id}) было отправлено фото: {photo.path}")
    await bot.send_photo(message.chat.id, photo)


def download_photo_telegram(dp: Dispatcher) -> None:
    """
    ! Telegram message register: Регистрация сообщений для скачивания и отправления фотографий для дальнейшей обработки
    """
    dp.message.register(download_photo_from_bot, F.photo)
    dp.message.register(photo_message, Command(commands=['photo']))
