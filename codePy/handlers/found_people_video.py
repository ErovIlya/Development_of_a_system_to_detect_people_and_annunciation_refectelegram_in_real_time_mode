from codePy.telegram_bot.new_loop import create_new_loop, stop_new_loop, get_status_on_new_loop
from codePy.telegram_bot.create_bot import dp, bot
from codePy.telegram_bot.state_for_bot import Form
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import types


async def start_found_people_for_bot(message: types.Message, state: FSMContext):
    path = '../input/video/test_video_5.mkv'
    await bot.send_message(message.chat.id, text='Поиск начнётся через несколько секунд')
    await create_new_loop(path, message.chat.id)
    await state.set_state(Form.start)


async def stop_found_people_for_bot(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Цикл скоро завершится")
    await stop_new_loop(query.from_user.id)
    await state.clear()


async def send_status_for_bot(query: types.CallbackQuery):
    await get_status_on_new_loop(query.from_user.id)


def found_people_on_video_telegram():
    dp.message.register(start_found_people_for_bot, Command(commands=['start']))
    dp.message.register(stop_found_people_for_bot, Command(commands=['stop']), Form.start)
    dp.message.register(send_status_for_bot, Command(commands=['status']), Form.start)
