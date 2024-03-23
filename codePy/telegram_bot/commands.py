from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='hi', description='Приветствие'),
        BotCommand(command='info', description='Краткая информация о боте'),
        BotCommand(command='photo', description='Результат поиска людей на текущей фотографии'),
        BotCommand(command='system', description='Краткая информация о системе'),
        BotCommand(command='start', description='Начало работы программы'),
        BotCommand(command='stop', description='Конец работы программы'),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
