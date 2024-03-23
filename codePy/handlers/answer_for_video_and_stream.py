from codePy.telegram_bot.create_bot import bot
from aiogram.types import InputFile


async def answer_text_message_from_video_and_stream(chat_id, text_message):
    await bot.send_message(chat_id, text_message)


async def answer_photo_message_from_video_and_stream(chat_id, path_photo):
    photo = InputFile(path_photo)
    await bot.send_photo(chat_id=chat_id, photo=photo)
