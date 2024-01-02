from codePy.handlers import download_photo, send_photo, simple_answer, found_people_video, system_info
from aiogram import executor
from codePy.telegram_bot.create_bot import dp


async def on_startup(_):
    print('Бот в данный момент онлайн')


simple_answer.hello_send_in_telegram(dp)
send_photo.send_photo_in_telegram(dp)
download_photo.download_photo_telegram(dp)
found_people_video.found_people_on_video_telegram()
system_info.system_message_in_telegram(dp)


def start_bot():
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
