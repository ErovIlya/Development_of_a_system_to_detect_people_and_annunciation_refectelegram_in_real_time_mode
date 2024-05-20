from codePy.telegram_bot.create_bot import dp, bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext


async def clear_status(chat_id: int) -> None:
    """
    Очищает состояния пользователя без удаления его временных данных
    :param chat_id: ID чата/пользователя, у которого нужно очистить состояния
    """
    user_key = StorageKey(bot.id, chat_id, chat_id)
    current_state = FSMContext(dp.storage, user_key)

    data = await current_state.get_data()
    await current_state.clear()
    await current_state.set_data(data)
