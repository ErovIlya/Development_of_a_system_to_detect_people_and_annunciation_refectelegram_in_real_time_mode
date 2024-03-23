from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


TOKEN_API = '6681684201:AAEV2k7LiE6uQiveEdt4m2bfbYkrW3Bzpjs'    # '6007241886:AAGofpJZje5CEB2cBUtElFVBNgN6XlMEf9U'
storage = MemoryStorage()

bot = Bot(token=TOKEN_API)
dp = Dispatcher(storage=storage)
