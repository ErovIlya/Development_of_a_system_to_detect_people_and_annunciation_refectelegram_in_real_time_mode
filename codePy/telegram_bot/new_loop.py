from codePy.yolo_model.found_people_on_real_time import start_found_people_on_stream
from codePy.handlers.simple_answer import send_message_for_interim_step
import threading


list_chat_id_and_thread_id = {}
list_chat_id_and_status = {}
stop_loop = {}


async def get_status_on_new_loop(chat_id):
    if chat_id in list_chat_id_and_thread_id:
        thread_id = list_chat_id_and_thread_id[chat_id]

        for thread in threading.enumerate():
            if thread.ident == thread_id:
                await send_message_for_interim_step(chat_id, 'Статус')
                if chat_id in list_chat_id_and_status:
                    list_chat_id_and_status[chat_id].set()
                break
    else:
        await send_message_for_interim_step(chat_id, 'Не введена команда "start"')


async def create_new_loop(path, chat_id):
    stop_event = threading.Event()
    status_event = threading.Event()
    new_thread = threading.Thread(target=start_found_people_on_stream, args=(path, chat_id, stop_event, status_event))
    new_thread.start()

    list_chat_id_and_thread_id[chat_id] = new_thread.ident
    stop_loop[chat_id] = stop_event
    list_chat_id_and_status[chat_id] = status_event

    print(new_thread.ident)


async def stop_new_loop(chat_id):
    if chat_id in list_chat_id_and_thread_id:
        thread_id = list_chat_id_and_thread_id[chat_id]

        for thread in threading.enumerate():
            if thread.ident == thread_id:
                await send_message_for_interim_step(chat_id, 'Остановка завершена')
                if chat_id in stop_loop:
                    stop_loop[chat_id].set()
                break
    else:
        await send_message_for_interim_step(chat_id, 'Не введена команда "start"')
