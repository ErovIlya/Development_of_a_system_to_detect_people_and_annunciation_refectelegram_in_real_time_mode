from codePy.handlers import download_photo, simple_answer, found_people_video, download_video, set_points
from codePy.telegram_bot.commands import set_commands
from codePy.telegram_bot.create_bot import dp, bot
from codePy.utils.unload_files_on_cloud import connect_to_mail
from codePy.utils.loggind_file import log_info


async def on_startup() -> None:
    """
    Действия при первом запуске бота
    """
    log_info("Бот в сети")
    connect_to_mail()


simple_answer.hello_send_in_telegram(dp)
download_photo.download_photo_telegram(dp)
found_people_video.found_people_on_video_telegram(dp)
download_video.download_video(dp)
set_points.set_points_for_video(dp)

dp.startup.register(on_startup)


async def start_bot() -> None:
    """
    Запуск телеграмм-бота
    """
    try:
        await set_commands(bot)
        await dp.start_polling(bot)
    finally:
        bot.session.close()
