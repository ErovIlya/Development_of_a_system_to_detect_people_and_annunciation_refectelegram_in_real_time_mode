from codePy.telegram_bot.new_loop import (create_new_loop_for_task_1, create_new_loop_for_task_2,
                                          stop_new_loop, get_status_on_new_loop)
from codePy.telegram_bot.create_bot import dp, bot
from codePy.telegram_bot.state_for_bot import Form
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import types


async def start_task_1_for_found_people_for_bot(message: types.Message, state: FSMContext):
    _state = await state.get_state()
    if _state == Form.start:
        await bot.send_message(message.chat.id, text="Поиск уже начался")
        return 
    await state.set_state(Form.start)
    path = '../input/video/video_task_1.mkv'
    await bot.send_message(message.chat.id, text='Поиск начнётся через несколько секунд')
    await create_new_loop_for_task_1(path, message.chat.id)


async def start_task_2_for_found_people_for_bot(message: types.Message, state: FSMContext):
    _state = await state.get_state()
    if _state == Form.start:
        await bot.send_message(message.chat.id, text="Поиск уже начался")
        return
    await state.set_state(Form.start)
    path = '../input/video/video_task_2.mkv'
    await bot.send_message(message.chat.id, text='Поиск начнётся через несколько секунд')
    await create_new_loop_for_task_2(path, message.chat.id)


async def stop_found_people_for_bot(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Цикл скоро завершится")
    await stop_new_loop(query.from_user.id)
    await state.clear()


async def send_status_for_bot(query: types.CallbackQuery):
    await get_status_on_new_loop(query.from_user.id)


def found_people_on_video_telegram():
    dp.message.register(start_task_1_for_found_people_for_bot, Command(commands=['task1']))
    dp.message.register(start_task_2_for_found_people_for_bot, Command(commands=['task2']))
    dp.message.register(stop_found_people_for_bot, Command(commands=['stop']), Form.start)
    dp.message.register(send_status_for_bot, Command(commands=['status']), Form.start)
