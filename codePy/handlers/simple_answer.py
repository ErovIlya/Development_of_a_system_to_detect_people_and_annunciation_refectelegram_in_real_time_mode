from codePy.utils.remove_files import remove_files
from codePy.utils.loggind_file import log_info
from codePy.telegram_bot.create_bot import bot
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher
from aiogram.filters import Command
import torch


hello = """
/hi - приветствие;
/info - краткая информация о боте;
/system - краткая информация о системе:
/photo - результат предыдущего поиска людей на фотографии;
При отправке фото будет произведён поиск людей;
При отправке видео файла будет начато создание пользовательской задачи детектирования людей
/download - Выгрузка видео файла на облако, если файл лишком большой (больше 20 МБайтов)
/set_line - Установка отрезка для пользовательской задачи
/set_zone - Установка зоны для пользовательской задачи
/set_point - Установка специализированной точки, по которой будет осуществляться детектирование
/next - Запуск пользовательской задачи
/task1 - Запуск детектирования людей на видео файле
/task2 - Запуск детектирования людей на видео файле с зоной и отрезком (пользовательская задача, если была создана)
"""


async def send_message_error_in_stop(chat_id, text_message) -> None:
    """
    ! Telegram: Отправка сообщений об ошибке или важного сообщения
    """
    await bot.send_message(chat_id, text_message)


async def hi_message(message: types.Message, state) -> None:
    """
    ! Telegram handler [/hi]: Приветствие пользователю
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/hi'")
    await message.answer(f"Привет, {message.from_user.full_name}")


async def info_message(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/info]: Отправка пользователю информации о боте
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/info'")
    await message.answer(hello)


async def clear_old_files(message: types.Message) -> None:
    """
    ! Telegram handler [/clear]: Удаление старых файлов на сервере и в облаке
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/clear'")
    remove_files()


system_text = f"Cuda доступна: {torch.cuda.is_available()};\n" \
    f"Версия CUDA: {torch.version.cuda};\n" \
    f"Версия cuDNN: {torch.backends.cudnn.version()};\n" \
    f"CuDNN включена: {torch.backends.cudnn.enabled};\n" \
    f"Число доступных устройств: {torch.cuda.device_count()};\n" \
    f"Устройство, которое функционирует сейчас: {torch.cuda.get_device_name(torch.cuda.current_device())}."


async def system_message(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/system]: Оправка информации о системе
    """
    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/system'")
    await bot.send_message(message.chat.id, system_text)


def system_message_in_telegram(dp: Dispatcher) -> None:
    """
    ! Telegram message register: Регистрация сообщений для отправки пользователю информации об системе
    """
    dp.message.register(system_message, Command(commands=['system']))


def hello_send_in_telegram(dp: Dispatcher) -> None:
    """
    ! Telegram message register: Регистрация сообщений для простых текстовых ответов
    """
    dp.message.register(hi_message, Command(commands=['hi']))
    dp.message.register(info_message, Command(commands=['info']))
    dp.message.register(clear_old_files, Command(commands=['clear']))
    dp.message.register(system_message, Command(commands=['system']))
