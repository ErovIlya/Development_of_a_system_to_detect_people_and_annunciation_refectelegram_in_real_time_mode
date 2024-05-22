from utils.unload_files_on_cloud import download_default_image, download_default_video1, download_default_video2
from telegram_bot.bot_telegram import start_bot
import utils.database as db
import asyncio
import os


def check_and_download_files() -> None:
    """
    Проверка и скачивание файлов по умолчанию
    :return:
    """
    if not os.path.exists('../input'):
        os.mkdir('../input')
    if not os.path.exists('../input/image'):
        os.mkdir('../input/image')
    if not os.path.exists('../input/image/default.png'):
        download_default_image()

    if not os.path.exists('../input/video'):
        os.mkdir('../input/video')
    if not os.path.exists('../input/video/video_task_1.mkv'):
        download_default_video1()

    if not os.path.exists('../input/video/video_task_1.mkv'):
        download_default_video2()


def main() -> None:
    # db.drop_tables()
    db.create_database()
    check_and_download_files()
    asyncio.run(start_bot())


if __name__ == '__main__':
    main()
