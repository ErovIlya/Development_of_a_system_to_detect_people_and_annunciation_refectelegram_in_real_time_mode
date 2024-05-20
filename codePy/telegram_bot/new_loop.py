from codePy.yolo_model.found_and_counting_people_on_real_timer import start_execution_task2
from codePy.yolo_model.found_people_on_real_time import start_found_people_on_stream
from codePy.handlers.simple_answer import send_message_error_in_stop
from codePy.utils.classes import User, StateForTask2, StateForTask1
import threading


list_chat_id_and_thread_id = {}
list_chat_id_and_status = {}
stop_loop = {}


async def create_new_loop_for_task(path: str, chat_id: int, state: int) -> None:
    """
    Создание потока для выполнения задачи 1
    :param path: относительный путь к видео файлу
    :param chat_id: ID чата/Пользователя, запустившего задачу
    :param state: Какую задачу запустил пользователь (utils/classes/StateForTask...)
    """
    stop_event = threading.Event()
    status_event = threading.Event()
    user = User(chat_id, stop_event, status_event)

    if state in [StateForTask1.stream(), StateForTask1.search()]:
        new_thread = threading.Thread(target=start_found_people_on_stream, args=(path, user, state))
        new_thread.start()
        list_chat_id_and_thread_id[chat_id] = new_thread.ident
    elif state in [StateForTask2.stream(), StateForTask2.search()]:
        new_thread = threading.Thread(target=start_execution_task2, args=(path, user, state))
        new_thread.start()
        list_chat_id_and_thread_id[chat_id] = new_thread.ident

    stop_loop[chat_id] = stop_event
    list_chat_id_and_status[chat_id] = status_event


async def stop_new_loop(chat_id: int) -> None:
    """
    Остановка выполнения задачи
    :param chat_id: ID чата/Пользователя, отменяющего задачу
    """
    if chat_id in list_chat_id_and_thread_id:
        thread_id = list_chat_id_and_thread_id[chat_id]

        for thread in threading.enumerate():
            if thread.ident == thread_id:
                await send_message_error_in_stop(chat_id, 'Остановка завершена')
                if chat_id in stop_loop:
                    stop_loop[chat_id].set()
                    thread.join()
                break
    else:
        await send_message_error_in_stop(chat_id, 'Не введена команда "/start"')


async def get_status_on_new_loop(chat_id: int) -> None:
    """
    Вывод промежуточного итога выполняемой задачи
    :param chat_id: ID чата/Пользователя, отменяющего задачу
    :return:
    """
    if chat_id in list_chat_id_and_thread_id:
        thread_id = list_chat_id_and_thread_id[chat_id]

        for thread in threading.enumerate():
            if thread.ident == thread_id:
                if chat_id in list_chat_id_and_status:
                    list_chat_id_and_status[chat_id].set()
                break
    else:
        await send_message_error_in_stop(chat_id, 'Не введена команда "/start"')
