from codePy.utils.unload_files_on_cloud import remove_files_cloud
from codePy.utils.loggind_file import log_info, log_error
import codePy.utils.database as db
from datetime import datetime
import shutil
import os


def remove_files() -> None:
    """
    Удаление старых (более 2 дней) файлов с сервера и облака
    """
    remove_files_in_server()
    remove_files_in_db()
    remove_files_in_cloud()


def remove_files_in_server() -> None:
    """
    Удаление старых (более 2 дней) файлов с сервера
    """
    try:
        _now_date = datetime.now()
        for directory in ['../download/photo', '../download/video', '../output/from_image', '../output/from_video',
                          '../output/from_video/first_frame', '../output/video']:
            if not os.path.exists(directory):
                continue
            for file in os.scandir(directory):
                if os.path.isdir(file.path):
                    _t_file = file.name
                else:
                    _t_file = file.name.split('.')[0]
                    _t_file = file.name.split('_')[0]
                _file = _t_file.split('-')
                if not (len(_file) >= 3):
                    continue

                _file_date = datetime(year=int(_file[2]), month=int(_file[1]), day=int(_file[0]))
                if (_now_date - _file_date).days > 2:
                    if os.path.isdir(file.path):
                        log_info(f"Директория {file.path} удалена")
                        shutil.rmtree(file.path)
                    else:
                        log_info(f"Файл {file.path} удалён")
                        os.remove(file.path)
    except Exception as e:
        log_error(e)


def remove_files_in_cloud() -> None:
    """
    Удаление старых (более 2 дней) файлов с облака
    """
    try:
        remove_files_cloud()
    except Exception as e:
        log_error(e)


def remove_files_in_db() -> None:
    try:
        db.delete_old_photo_and_video()
    except Exception as e:
        log_error(e)
