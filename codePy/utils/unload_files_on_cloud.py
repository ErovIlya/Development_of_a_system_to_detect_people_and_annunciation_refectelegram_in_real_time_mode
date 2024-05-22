from codePy.utils.create_path_for_files import create_path_for_download_video
from codePy.utils.loggind_file import log_info, log_error
from datetime import datetime
import webdav.client as wc
import os


def create_client() -> wc.Client:
    """
    Создание клиента для подключения к облаку
    :return: объект класса webdav.client
    """
    data = {
        'webdav_hostname': "https://webdav.cloud.mail.ru",
        'webdav_login':    "tortoiskiki5@bk.ru",
        'webdav_password': "gy5sRLFVaqad8SFdwSxe"
    }
    return wc.Client(data)


def download_video_cloud(file_name: str) -> str:
    """
    Скачивание входящего видео с облака
    :param file_name: название файла
    :return: относительный путь к файлу на сервере
    """
    client = create_client()
    try:
        remote_path = '/telegram/input/' + file_name
        local_path = create_path_for_download_video()
        client.download_file(remote_path=remote_path, local_path=local_path)
        log_info(f"Скачан файл {local_path} из облака")
        return local_path
    except Exception as e:
        log_error(e)
        return '/'
    finally:
        del client


def create_dir_in_cloud(path: str) -> str:
    client = create_client()
    file_name = path.split('/')[-1]
    file_date = path.split('/')[-2]
    remote_path = f"telegram/output/{file_date}/{file_name}"

    if not client.check('telegram'):
        client.mkdir('telegram')

    if not client.check('telegram/output'):
        client.mkdir('telegram/output')

    if not client.check(f'telegram/output/{file_date}'):
        client.mkdir(f'telegram/output/{file_date}')
        print(client.publish(f'telegram/output/{file_date}'))

    del client
    return remote_path


def unload_file_in_cloud(path: str) -> str:
    """
    Выгрузка файла на облако
    :param path: Относительный путь к файлу на сервере
    :return: Относительный путь к файлу на облаке
    """
    remote_path = create_dir_in_cloud(path)
    client = create_client()

    client.upload_sync(
        remote_path=remote_path,
        local_path=os.path.abspath(path)
    )
    print(client.list('telegram/output'))
    log_info(f"Файл {path} Успешно выгружен на облако")
    "print(client.publish(remote_path))"
    del client

    return remote_path


def connect_to_mail() -> None:
    """
    Подключение к облаку
    """
    client = create_client()
    if not client.check('telegram'):
        client.mkdir('telegram')
    my_files = client.list('telegram')

    del client
    print(my_files)
    log_info("Подключение к облаку успешно")


def remove_files_cloud() -> None:
    """
    Удаление старых (более 2 дней) отправленных файлов на облаке
    """
    client = create_client()
    list_files = client.list('telegram')
    _now_date = datetime.now()

    for file in list_files:
        _file = file.split('-')
        _file_date = datetime(year=int(_file[2]), month=int(_file[1]), day=int(_file[0]))
        if (_now_date - _file_date).days > 2:
            log_info(f"Удалена директория 'telegram/{file}' из облака")
            client.clean(f"telegram/{file}")

    del client


def download_default_image() -> None:
    """
    Скачивание default.png из облака
    """
    client = create_client()
    try:
        remote_path = '/telegram/files_for_download/default.png'
        local_path = '../input/image/default.png'
        client.download_file(remote_path=remote_path, local_path=local_path)
        log_info(f"Скачан файл {local_path} из облака")
    except Exception as e:
        log_error(e)
    finally:
        del client


def download_default_video1() -> None:
    """
    Скачивание video_task_1.mkv из облака
    """
    client = create_client()
    try:
        remote_path = '/telegram/files_for_download/video_task_1.mkv'
        local_path = '../input/video/video_task_1.mkv'
        client.download_file(remote_path=remote_path, local_path=local_path)
        log_info(f"Скачан файл {local_path} из облака")
    except Exception as e:
        log_error(e)
    finally:
        del client


def download_default_video2() -> None:
    """
    Скачивание video_task_2.mkv из облака
    """
    client = create_client()
    try:
        remote_path = '/telegram/files_for_download/video_task_2.mkv'
        local_path = '../input/video/video_task_2.mkv'
        client.download_file(remote_path=remote_path, local_path=local_path)
        log_info(f"Скачан файл {local_path} из облака")
    except Exception as e:
        log_error(e)
    finally:
        del client
