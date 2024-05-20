from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram import Bot


async def set_commands(bot: Bot) -> None:
    """
    Установка команд для телеграмм-бота
    """
    commands = [
        BotCommand(command='hi', description='Приветствие'),
        BotCommand(command='info', description='Краткая информация о боте'),
        BotCommand(command='photo', description='Результат поиска людей на текущей фотографии'),
        BotCommand(command='system', description='Краткая информация о системе'),
        BotCommand(command='task1', description='Первое задание (поиск людей в видео потоке)'),
        BotCommand(command='video_task1', description='Первое задание, но загрузка результата в видеофайл'),
        BotCommand(command='task2', description='Второе задание (поиск людей в области видео потоке и подсчёт)'),
        BotCommand(command='video_task2', description='Второе задание, но загрузка результата в видеофайл'),
        BotCommand(command='status', description='Статус выполнения задачи'),
        BotCommand(command='stop', description='Конец работы программы'),
        BotCommand(command='clear', description='Удаление старых (от двух и более дней) файлов на сервере и облаке'),
        BotCommand(command='download', description='Отправка видео для работы программы'),
        BotCommand(command='set_points', description='Установка точек для линии'),
        BotCommand(command='next', description='Запуск пользовательской задачи'),
        BotCommand(command='cancel', description='Отмена этапа пользовательской задачи')
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
