from codePy.handlers import download_photo, send_photo, simple_answer, found_people_video, system_info, download_video
from codePy.telegram_bot.create_bot import dp, bot
from codePy.telegram_bot.commands import set_commands
from codePy.unload_video import connect_to_mail


async def on_startup():
    print('Бот в данный момент онлайн')
    connect_to_mail()


simple_answer.hello_send_in_telegram(dp)
send_photo.send_photo_in_telegram(dp)
download_photo.download_photo_telegram(dp)
found_people_video.found_people_on_video_telegram(dp)
system_info.system_message_in_telegram(dp)
download_video.download_video(dp)

dp.startup.register(on_startup)


async def start_bot():
    try:
        await set_commands(bot)
        await dp.start_polling(bot)
    finally:
        bot.session.close()
