from datetime import datetime
import logging


logging.basicConfig(level=logging.INFO, filename="../logging_file.txt", filemode="w")


def log_info(text) -> None:
    """
    Логирование входящего текста в файл
    """
    logging.info(f"[{datetime.now()}]" + text)


def log_error(err: Exception) -> None:
    """
    Логирование ошибки в файл
    """
    logging.error(f"[{datetime.now()}]" + str(err))
