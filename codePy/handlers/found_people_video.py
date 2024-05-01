from codePy.telegram_bot.new_loop import stop_new_loop, get_status_on_new_loop, create_new_loop_for_task
from codePy.telegram_bot.keyboard import get_keyboard
from codePy.classes import StateForTask2, StateForTask1
from codePy.telegram_bot.create_bot import bot
from codePy.telegram_bot.state_for_bot import Form
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import types, Dispatcher


def check_task(state: FSMContext) -> bool:
    _state = state.get_state()
    return _state in [Form.start, Form.point_state, Form.search, Form.point_test, Form.download]


async def start_task_1_for_found_people_for_bot(message: types.Message, state: FSMContext):
    if check_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return 
    await state.set_state(Form.start)
    path = '../input/video/video_task_1.mkv'
    await bot.send_message(
        message.chat.id,
        text='Поиск начнётся через несколько секунд',
        reply_markup=get_keyboard(Form.start)
    )
    await create_new_loop_for_task(path, message.chat.id, StateForTask1.stream())


async def download_video_for_task_1(message: types.Message, state: FSMContext):
    if check_task(state):
        await bot.send_message(message.chat.id,
                               text="Загрузка видео не может начаться во время запущенной задачи",
                               reply_markup=get_keyboard(await state.get_state()))
        return
    await state.set_state(Form.search)
    path = '../input/video/video_task_1.mkv'
    await create_new_loop_for_task(path, message.chat.id, StateForTask1.search())


async def start_task_2_for_found_people_for_bot(message: types.Message, state: FSMContext):
    if check_task(state):
        await bot.send_message(
            message.chat.id,
            text="Запущена другая задача",
            reply_markup=get_keyboard(await state.get_state())
        )
        return
    await state.set_state(Form.start)
    path = '../input/video/video_task_2.mkv'
    await bot.send_message(
        message.chat.id,
        text='Поиск начнётся через несколько секунд',
        reply_markup=get_keyboard(Form.start)
    )
    await create_new_loop_for_task(path, message.chat.id, StateForTask2.stream())


async def download_video_for_task_2(message: types.Message, state: FSMContext):
    if check_task(state):
        await bot.send_message(
            message.chat.id,
            text="Загрузка видео не может начаться во время другой запущенной задачи",
            reply_markup=get_keyboard(await state.get_state())
        )
        return
    await state.set_state(Form.search)
    path = '../input/video/video_task_2.mkv'
    await create_new_loop_for_task(path, message.chat.id, StateForTask2.search())


async def stop_found_people_for_bot(message: types.Message, state: FSMContext):
    await message.reply("Цикл скоро завершится")
    await stop_new_loop(message.chat.id)
    await state.clear()


async def send_status_for_bot(query: types.CallbackQuery):
    await get_status_on_new_loop(query.from_user.id)


def found_people_on_video_telegram(dp: Dispatcher):
    dp.message.register(start_task_1_for_found_people_for_bot, Command(commands=['task1']))
    dp.message.register(start_task_2_for_found_people_for_bot, Command(commands=['task2']))
    dp.message.register(download_video_for_task_2, Command(commands=['video_task2']))
    dp.message.register(download_video_for_task_1, Command(commands=['video_task1']))
    dp.message.register(stop_found_people_for_bot, Command(commands=['stop']), Form.start)
    dp.message.register(send_status_for_bot, Command(commands=['status']), Form.start)
