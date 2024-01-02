from codePy.telegram_bot.create_bot import bot
import datetime


async def send_message(chat_id, text_message):
    print("Что-то отправляется")
    await bot.send_message(chat_id, text_message)


async def send_photo_ot_the_found_people(chat_id, path_image):
    text = f"Внимание, сегодня, {datetime.datetime.now().strftime('%d-%m-%Y')} " \
           f"в {datetime.datetime.now().strftime('%H.%M.%S')} " \
           f"найден человек на видеокамере:"

    bot.send_message(chat_id, text)
