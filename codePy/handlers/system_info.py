from codePy.telegram_bot.create_bot import bot
from aiogram import types, Dispatcher
import torch


system_text = f"Cuda доступна: {torch.cuda.is_available()};\n" \
    f"Версия CUDA: {torch.version.cuda};\n" \
    f"Версия cuDNN: {torch.backends.cudnn.version()};\n" \
    f"CuDNN включена: {torch.backends.cudnn.enabled};\n" \
    f"Число доступных устройств: {torch.cuda.device_count()};\n" \
    f"Устройство, которое функционирует сейчас: {torch.cuda.get_device_name(torch.cuda.current_device())}."


async def system_message(message: types.Message):
    await bot.send_message(message.chat.id, system_text)


def system_message_in_telegram(dp: Dispatcher):
    dp.register_message_handler(system_message, commands=['system'])
