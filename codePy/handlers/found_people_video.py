from codePy.telegram_bot.new_loop import stop_new_loop, get_status_on_new_loop, create_new_loop_for_task
from codePy.utils.classes import StateForTask2, StateForTask1
from codePy.telegram_bot.state_for_bot import Form
from codePy.telegram_bot.create_bot import bot
from codePy.utils.loggind_file import log_info
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher
from aiogram.filters import Command
import codePy.utils.database as db


async def check_task(state: FSMContext) -> bool:
    """
    ! Telegram: Проверка, что пользователь начал выполнять какое-либо задание:
    поиск объектов в видео потоке (преобразование в видео или в реальном времени),
    подготовка к скачиванию видео файла или создание пользовательской задачи
    :return: true - если задание от пользователя выполняется, false - нет
    """
    _state = await state.get_state()
    return _state in [
        Form.start, Form.search, Form.download,
        Form.line_state, Form.line_test, Form.zone_state, Form.zone_test
                      ]


async def start_task_1_for_found_people_for_bot(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/stream1]: Запуск задачи 1 (детектирование людей в видео файле)
    """
    if await check_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return 
    await state.set_state(Form.start)

    path = db.get_video_path(message.chat.id)
    if path is None:
        path = '../input/video/video_task_1.mkv'

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) начал выполнения задачи "
             f"детектирования (задача №1) видео файла '{path}' в реальном времени")

    await bot.send_message(
        message.chat.id,
        text='Поиск начнётся через несколько секунд'
    )
    await create_new_loop_for_task(message.chat.id, StateForTask1.stream())


async def download_video_for_task_1(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/task1]: Запуск задачи 1 (детектирование людей в видео файле)
    для преобразования в выходной видео файл
    """
    if await check_task(state):
        await bot.send_message(message.chat.id,
                               text="Загрузка видео не может начаться во время запущенной задачи")
        return
    await state.set_state(Form.search)

    path = db.get_video_path(message.chat.id)
    if path is None:
        path = '../input/video/video_task_1.mkv'

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) начал выполнения задачи "
             f"детектирования (задача №1) видео файла '{path}' и преобразования в выходной видеофайл")

    await create_new_loop_for_task(message.chat.id, StateForTask1.search())


async def start_task_2_for_found_people_for_bot(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/stream2]: Запуск задачи 2 (детектирование людей и поиск пересечения с отрезком в видео файле)
    """
    if await check_task(state):
        await bot.send_message(
            message.chat.id,
            text="Запущена другая задача"
        )
        return
    await state.set_state(Form.start)

    path = db.get_video_path(message.chat.id)
    if path is None:
        path = '../input/video/video_task_2.mkv'

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) начал выполнения задачи "
             f"детектирования и пересечении линии (задача №2) видео файла '{path}' в реальном времени")

    await bot.send_message(
        message.chat.id,
        text='Поиск начнётся через несколько секунд'
    )
    await create_new_loop_for_task(message.chat.id, StateForTask2.stream())


async def download_video_for_task_2(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/task2]: Запуск задачи 2 (детектирование людей и поиск пересечения с отрезком в видео
    файле) для преобразования в выходной видео файл
    """
    if await check_task(state):
        await bot.send_message(
            message.chat.id,
            text="Загрузка видео не может начаться во время другой запущенной задачи"
        )
        return
    await state.set_state(Form.search)

    path = db.get_video_path(message.chat.id)
    if path is None:
        path = '../input/video/video_task_2.mkv'

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) начал выполнения задачи "
             f"детектирования и пересечении линии (задача №2) видео файла '{path}' "
             f"и преобразования в выходной видеофайл")

    await create_new_loop_for_task(message.chat.id, StateForTask2.search())


async def stop_found_people_for_bot(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/stop]: Остановка выполнения задачи детектирования (задача 1 и задача 2)
    """
    await message.reply("Цикл скоро завершится")

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/stop'")

    if state.get_state() == Form.start:
        await stop_new_loop(message.chat.id)
        await state.clear()


async def send_status_for_bot(message: types.Message, state: FSMContext):
    """
    ! Telegram handler [/status]: Отправка статуса выполняемой задачи
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/status'")
    if state.get_state() == Form.start:
        await get_status_on_new_loop(message.from_user.id)


def found_people_on_video_telegram(dp: Dispatcher):
    """
    ! Telegram message register: Регистрация сообщений для выполнения, остановки и получения "статуса" задачи 1 и 2
    """
    # dp.message.register(start_task_1_for_found_people_for_bot, Command(commands=['stream1']))
    # dp.message.register(start_task_2_for_found_people_for_bot, Command(commands=['stream2']))
    dp.message.register(download_video_for_task_2, Command(commands=['task2']))
    dp.message.register(download_video_for_task_1, Command(commands=['task1']))
    # dp.message.register(stop_found_people_for_bot, Command(commands=['stop']), Form.start)
    # dp.message.register(stop_found_people_for_bot, Command(commands=['stop']), Form.search)
    # dp.message.register(send_status_for_bot, Command(commands=['status']), Form.start)
