from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


TOKEN_API = '6007241886:AAGofpJZje5CEB2cBUtElFVBNgN6XlMEf9U'
storage = MemoryStorage()

bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)
