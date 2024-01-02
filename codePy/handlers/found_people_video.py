from codePy.telegram_bot.new_loop import create_new_loop, stop_new_loop, get_status_on_new_loop
from codePy.telegram_bot.create_bot import dp, bot
from codePy.telegram_bot.state_for_bot import Form
from aiogram.dispatcher import FSMContext
from aiogram import types


async def start_found_people_for_bot(message: types.Message, state: FSMContext):
    path = 'input/video/test_video_5.mkv'
    await bot.send_message(message.chat.id, text='Поиск начнётся через несколько секунд')
    await create_new_loop(path, message.chat.id)
    # await found_people_from_stream(path, message.chat.id)
    await state.set_state(Form.start)


async def stop_found_people_for_bot(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Цикл скоро завершится")
    await stop_new_loop(query.from_user.id)
    await state.finish()


async def send_status_for_bot(query: types.CallbackQuery):
    await get_status_on_new_loop(query.from_user.id)
    pass


def found_people_on_video_telegram():
    dp.register_message_handler(start_found_people_for_bot, commands=['start'])
    dp.register_message_handler(stop_found_people_for_bot, commands=['stop'], state=Form.start)
    dp.register_message_handler(send_status_for_bot, commands=['status'], state=Form.start)
