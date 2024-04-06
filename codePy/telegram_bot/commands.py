from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='hi', description='Приветствие'),
        BotCommand(command='info', description='Краткая информация о боте'),
        BotCommand(command='photo', description='Результат поиска людей на текущей фотографии'),
        BotCommand(command='system', description='Краткая информация о системе'),
        BotCommand(command='task1', description='Первое задание (поиск людей в видеопотоке)'),
        BotCommand(command='task2', description='Второе задание (поиск людей в области видеопотоке и подсчёт)'),
        BotCommand(command='stop', description='Конец работы программы'),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
