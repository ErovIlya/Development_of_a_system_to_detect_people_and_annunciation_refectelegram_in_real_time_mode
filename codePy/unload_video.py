import webdav.client as wc
import datetime
import pathlib
import os


data = {
 'webdav_hostname': "https://webdav.cloud.mail.ru",
 'webdav_login':    "tortoiskiki5@bk.ru",
 'webdav_password': "gy5sRLFVaqad8SFdwSxe"
}
client = wc.Client(data)


def unload_file_in_cloud(path: str) -> str:
    now_date = datetime.datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.datetime.now().strftime('%H-%M-%S')
    file_extension = pathlib.Path(path).suffix
    remote_path = f"telegram/{now_date}/{now_time}{file_extension}"

    if not client.check('telegram'):
        client.mkdir('telegram')

    if not client.check(f'telegram/{now_date}'):
        client.mkdir(f'telegram/{now_date}')

    client.upload_sync(
        remote_path=remote_path,
        local_path=os.path.abspath(path))
    print("Успешно")

    return remote_path


def connect_to_mail():
    if not client.check('telegram'):
        client.mkdir('telegram')
    my_files = client.list()
    print(my_files)

