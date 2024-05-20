from codePy.telegram_bot.keyboard import keyboard_after_download_video, keyboard_start, get_keyboard
from codePy.utils.create_path_for_files import create_path_for_download_video
from codePy.telegram_bot.new_loop import create_new_loop_for_task
from codePy.utils.unload_files_on_cloud import download_video_cloud
from codePy.utils.loggind_file import log_info, log_error
from codePy.telegram_bot.clear_status import clear_status
from codePy.telegram_bot.state_for_bot import Form
from codePy.telegram_bot.create_bot import bot
from codePy.utils.classes import StateForTask2
from aiogram.fsm.context import FSMContext
from aiogram import types, F, Dispatcher
from aiogram.filters import Command
import codePy.utils.database as db


async def check_task(state: FSMContext) -> bool:
    """
    ! Telegram: Проверка, что пользователь начал выполнять какое-либо задание:
    поиск объектов в видео потоке (преобразование в видео или в реальном времени)
    :return: true - если задание от пользователя выполняется, false - нет
    """
    _state = await state.get_state()
    return _state in [Form.start, Form.search, Form.download]


def check_format_video(file_name: str) -> bool:
    """
    Проверка формата файла (на данный момент это mp4 и mkv (вне зависимости от регистра))
    :param file_name: название (или путь к файлу) файла
    :return: true, если файл принадлежит к данному формату, false - нет
    """
    _file = file_name.split('.')
    print(_file)
    print(_file[-1].lower() in ['mkv', 'mp4'])
    return len(_file) != 2 or not _file[-1].lower() in ['mkv', 'mp4']


async def prep_to_download(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/download]: Подготовка к скачиванию видео
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/download'")
    await state.set_state(Form.download)
    await message.reply("В сообщение напишите название файла (поддерживается форматы mp4 и mkv)"
                        "(Ссылка на облако, куда необходимо выложить файл https://cloud.mail.ru/public/7nne/hQ3qdui7X)")


async def download_video_from_cloud(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Загрузка видео с облака от пользователя (принимает от пользователя имя выгруженного файла)
    """
    name_file = message.text
    if check_format_video(name_file):
        await message.reply("Неверный формат файла")
        return
    path = download_video_cloud(name_file)
    if path == '/':
        await message.reply("Файл не найден")
        return

    db.insert_video(message.chat.id, path)
    await state.clear()
    await message.reply(
        text=f"Видео успешно загрузилось.\nПуть к видео файлу: {path}",
        reply_markup=keyboard_after_download_video
    )


async def download_video_from_telegram(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Загрузка видео с телеграмма от пользователя
    """
    try:
        log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) отправил видеофайл")
        file_id = message.video.file_id
        file = await bot.get_file(file_id)

        path = create_path_for_download_video()

        await message.reply(text="Загрузка видео началась")
        await bot.download_file(file.file_path, path)

        await state.clear()
        db.insert_video(message.chat.id, path)

        await message.reply(
            text=f"Видео успешно загрузилось.\nПуть к видео файлу: {path}",
            reply_markup=keyboard_after_download_video
        )

        log_info(f"Скачан и сохранён файл '{path}'")
    except Exception as e:
        log_error(e)


async def start_task(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/next]: Старт пользовательской задачи пользователем
    """
    path = db.get_video_path(message.chat.id)
    if path is None or (await state.get_state() not in [Form.line_test, Form.zone_test]):
        await message.reply(
            text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео",
            reply_markup=get_keyboard(await state.get_state())
        )
        return

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/next'")

    await create_new_loop_for_task(path, message.chat.id, StateForTask2.search())

    await message.reply(text="Выполнение задачи началось", reply_markup=keyboard_start)
    await state.set_state(Form.search)


async def cancel(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/cancel]: Отмена данной задачи
    """
    _state = await state.get_state()
    if _state in [Form.line_state, Form.line_test, Form.download, Form.zone_state, Form.zone_test]:
        await clear_status(message.chat.id)

        log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/cancel'")
        await message.reply(text="Задача отменена", reply_markup=keyboard_start)


def download_video(dp: Dispatcher) -> None:
    """
    ! Telegram message register: Регистрация сообщений для загрузки и создания пользовательской задачи от пользователя
    """
    dp.message.register(cancel, Command(commands=['cancel']))
    dp.message.register(download_video_from_telegram, F.video)
    dp.message.register(prep_to_download, Command(commands=['download']))
    dp.message.register(download_video_from_cloud, Form.download)
    dp.message.register(start_task, Command(commands=['next']), Form.line_test)
    dp.message.register(start_task, Command(commands=['next']), Form.zone_test)
