import psycopg2


def create_conn():
    """
    Создание подключения
    """
    conn = psycopg2.connect(dbname='postgres', user='postgres',
                            password='12345', host='localhost')
    return conn


def create_database() -> None:
    """
    Создание всех таблиц и зависимостей в БД
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        "create table if not exists points( "   # Таблиц содержит информацию о созданных точках
        "row_id int primary key, "              # ID точки
        "chat_id int not null, "                # ID чата/пользователя, создавшего точку
        "x int not null, "                      # Х координата точки
        "y int not null, "                      # Y координата точки
        "task int not null "                    # Сведения о том, для чего нужна точка (0 - для отрезка, 1 - для зоны)
        "); "
        "create sequence if not exists seq_points start 1; "
        "alter table points alter column row_id set default nextval('seq_points'); "
        ""
        "create table if not exists lines( "    # Таблица содержит информацию о созданных отрезках
        "row_id int primary key, "              # ID отрезка
        "chat_id int not null, "                # ID чата/пользователя, создавшего отрезок
        "point_start int not null, "            # Точка начала отрезка
        "point_end int not null, "              # Точка конца отрезка
        "use int not null, "                    # Показывает, последний ли это добавленный отрезок (0 - старый,
                                                # 1 - предпоследний, 2 - последний)
        "foreign key (point_start) references points (row_id), "
        "foreign key (point_end) references points (row_id) "
        "); "
        "create sequence if not exists seq_lines start 1; "
        "alter table lines alter column row_id set default nextval('seq_lines'); "
        ""
        "create table if not exists zones( "    # Таблица содержит информацию о созданных зонах
        "row_id int primary key, "              # ID зоны
        "chat_id int not null, "                # ID чата/пользователя, создавшего зону
        "point1 int, "                          # Точка 1
        "point2 int, "                          # Точка 2
        "point3 int, "                          # Точка 3
        "point4 int, "                          # Точка 4
        "point5 int, "                          # Точка 5
        "use int not null, "                    # Показывает, последний ли это добавленная зона (0 - старый,
                                                # 1 - предпоследний, 2 - последний)
        "FOREIGN KEY (point1) REFERENCES points (row_id), "
        "FOREIGN KEY (point2) REFERENCES points (row_id), "
        "FOREIGN KEY (point3) REFERENCES points (row_id), "
        "FOREIGN KEY (point4) REFERENCES points (row_id), "
        "FOREIGN KEY (point5) REFERENCES points (row_id) "
        "); "
        "create sequence if not exists seq_zones start 1; "
        "alter table zones alter column row_id set default nextval('seq_zones'); "
        ""
        "create table if not exists video( "    # Таблица содержит информацию о выгруженных видео пользователей
        "row_id int primary key, "              # ID записи
        "chat_id int not null, "                # ID чата/пользователя, создавшего точку
        "path varchar(100) not null, "          # Путь к видео файлу
        "date timestamp  not null "             # Дата и время скачивания файла
        "); "
        "create sequence if not exists seq_video start 1; "
        "alter table video alter column row_id set default nextval('seq_video'); "
        ""
        "create table if not exists photo( "    # Таблица содержит информацию о выгруженных видео пользователей
        "row_id int primary key, "              # ID записи
        "chat_id int not null, "                # ID чата/пользователя, создавшего точку
        "path varchar(100) not null, "          # Путь к фотографии
        "date timestamp  not null "             # Дата и время скачивания файла
        "); "
        "create sequence if not exists seq_photo start 1; "
        "alter table photo alter column row_id set default nextval('seq_photo'); "
        ""
        "create table if not exists sp_points( "# Таблица содержит информацию о спец точках, установленных пользователем
        "row_id int primary key, "              # ID записи
        "chat_id int not null, "                # ID чата/пользователя, создавшего точку
        "point_info int not null "              # ID "особой" точки
        "); "
        "create sequence if not exists seq_sp_points start 1; "
        "ALTER TABLE sp_points ALTER COLUMN row_id SET DEFAULT nextval('seq_sp_points'); "
    )
    cursor.close()
    conn.commit()
    conn.close()


def insert_video(chat_id: int, path: str) -> int:
    """
    Добавление данных о видео файле в БД
    :param chat_id: ID чата/пользователя, отправившего видео файл
    :param path: относительный путь к файлу
    :return: возвращает её row_id в БД
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"insert into video (chat_id, path, date) "
        f"values ({chat_id}, '{path}', (SELECT NOW()::timestamp)) "
        f"returning row_id"
    )
    row_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return int(row_id[0])


def insert_photo(chat_id: int, path: str) -> int:
    """
    Добавление данных о фотографии в БД
    :param chat_id: ID чата/пользователя, отправившего видео файл
    :param path: относительный путь к файлу
    :return: возвращает её row_id в БД
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"insert into photo (chat_id, path, date) "
        f"values ({chat_id}, '{path}', (SELECT NOW()::timestamp)) "
        f"returning row_id"
    )
    row_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return int(row_id[0])


def insert_point(chat_id: int, x: int, y: int, task: int) -> int:
    """
    Добавление точки в БД
    :param chat_id: ID чата/пользователя, создавшего точку
    :param x: Х координата точки
    :param y: Y координата точки
    :param task: Для чего создавалась точка: 0 - для отрезка, 1 - для зоны
    :return: возвращает её row_id в БД
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"insert into points (chat_id, x, y, task) "
        f"values ({chat_id}, {x}, {y}, {task}) "
        f"returning row_id"
    )
    row_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return int(row_id[0])


def insert_sp_point(chat_id: int, id_point: int) -> int:
    """
    Добавление "особой" точки в БД
    :param chat_id: ID чата/пользователя, создавшего точку
    :param id_point: ID "особой" точки (смотри класс WhichPointObjectBeTracked)
    :return: возвращает её row_id в БД
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"insert into sp_points (chat_id, point_info) "
        f"values ({chat_id}, {id_point}) "
        f"returning row_id"
    )
    row_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return int(row_id[0])


def insert_line(chat_id: int, point_start: int, point_end: int) -> int:
    """
    Добавление отрезка в БД (при добавлении нового отрезка "удаляется" старый)
    :param chat_id: ID чата/пользователя, создавшего точку
    :param point_start: Точка начала отрезка
    :param point_end: Точка конца отрезка
    :return: возвращает её row_id в БД
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"DO "
        f"$do$ "
        f"begin "
        f"if exists(select * from lines where chat_id = {chat_id} and use = 2) then "
        f"update lines set use = 1 where chat_id = {chat_id} and use = 2; "
        f"end if; "
        f"if exists(select * from lines where chat_id = {chat_id} and use = 1) then "
        f"update lines set use = 0 where chat_id = {chat_id} and use = 1; "
        f"end if; "
        f"END "
        f"$do$ "
    )
    cursor.execute(
        f""
        f"insert into lines (chat_id, point_start, point_end, use) "
        f"values ({chat_id}, {point_start}, {point_end}, 2) "
        f"returning row_id "
    )
    row_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return int(row_id[0])


def insert_zone(chat_id: int, points: list[int]) -> int:
    """
    Добавление зоны в БД (при добавлении новой зоны "удаляется" старая)
    :param chat_id: ID чата/пользователя, создавшего точку
    :param points: id точек зоны в виде массива (от 3 до 5 точек)
    :return: возвращает её row_id в БД
    """
    point1 = points[0]
    point2 = points[1]
    point3 = points[2]
    point4 = points[3] if len(points) > 3 else 'null'
    point5 = points[4] if len(points) > 4 else 'null'

    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"DO "
        f"$do$ "
        f"begin "
        f"if exists(select * from zones where chat_id = {chat_id} and use = 2) then "
        f"update zones set use = 1 where chat_id = {chat_id} and use = 2; "
        f"end if; "
        f"if exists(select * from zones where chat_id = {chat_id} and use = 1) then "
        f"update zones set use = 0 where chat_id = {chat_id} and use = 1; "
        f"end if; "
        f"END "
        f"$do$ "
    )
    cursor.execute(
        f""
        f"insert into zones (chat_id, point1, point2, point3, point4, point5, use) "
        f"values ({chat_id}, {point1}, {point2}, {point3}, {point4}, {point5}, 2) "
        f"returning row_id "
    )

    row_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    return int(row_id[0])


def get_photo_path(chat_id: int) -> str:
    """
    Возвращает относительный путь к последней отправленной фотографии данным пользователем
    :param chat_id: ID чата/пользователя, создавшего точку
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"select path from photo "
        f"where chat_id = {chat_id} "
        f"order by date desc "
        f"limit 1 "
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return '../input/image/default.png'
    return row[0]


def get_video_path(chat_id: int) -> str or None:
    """
    Возвращает относительный путь к последнему отправленному видео файлу данным пользователем
    :param chat_id: ID чата/пользователя, создавшего точку
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"select path from video "
        f"where chat_id = {chat_id} "
        f"order by date desc "
        f"limit 1 "
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        return None
    return row[0]


def check_video_file(chat_id: int) -> bool:
    """
    Проверка, что пользователь выгружал видеофайл и о нём есть записи в БД
    :param chat_id: ID чата/пользователя, создавшего точку
    """
    path = get_video_path(chat_id)
    if path is None:
        return False
    return True


def get_sp_point(chat_id: int) -> int:
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"select row_id, point_info "
        f"from sp_points "
        f"where chat_id = {chat_id} "
        f"order by row_id desc "
        f"limit 1 "
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[1]


def get_line(chat_id: int) -> [int, int, int, int, int]:
    """
    Возвращает данные отрезка, созданного данным пользователем
    :param chat_id: ID чата/пользователя, создавшего точку
    :return: кортеж из 5 целых чисел [row_id данного отрезка,
    X координата первой точки, Y координата первой точки,
    X координата второй точки, Y координата второй точки]
    """
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"select l.row_id, p1.x, p1.y, p2.x, p2.y "
        f"from lines l "
        f"left join points p1 on l.point_start = p1.row_id "
        f"left join points p2 on l.point_end = p2.row_id "
        f"where l.chat_id = {chat_id} and use = 2 "
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_zone(chat_id) -> [int, int, int, int, int, int, int, int or None, int or None, int or None, int or None]:
    """
    Возвращает данные зоны, созданного данным пользователем
    :param chat_id: ID чата/пользователя, создавшего точку
    :return: кортеж из 5 целых чисел [row_id данного отрезка,
    X координата первой точки, Y координата первой точки,
    X координата второй точки, Y координата второй точки]
    """
    conn = create_conn()
    cursor = conn.cursor()

    cursor.execute(
        f"select z.row_id, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, p5.x, p5.y "
        f"from zones z "
        f"left join points p1 on z.point1 = p1.row_id "
        f"left join points p2 on z.point2 = p2.row_id "
        f"left join points p3 on z.point3 = p3.row_id "
        f"left join points p4 on z.point4 = p4.row_id "
        f"left join points p5 on z.point5 = p5.row_id "
        f"where z.chat_id = {chat_id} and use = 2 "
    )
    row = cursor.fetchall()
    cursor.close()
    conn.close()
    return row[0]


def drop_tables() -> None:
    """
    Удаление всех данных и таблиц из БД
    """
    conn = create_conn()
    cursor = conn.cursor()

    cursor.execute(
        "drop table if exists zones; "
        "drop table if exists lines; "
        "drop table if exists points; "
        "drop table if exists video; "
        "drop table if exists photo; "
        "drop sequence if exists seq_zones; "
        "drop sequence if exists seq_lines; "
        "drop sequence if exists seq_points; "
        "drop sequence if exists seq_video; "
        "drop sequence if exists seq_photo; "
    )
    cursor.close()
    conn.commit()
    conn.close()


def delete_old_photo_and_video():
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        "delete from video "
        "where extract(day from (SELECT NOW()::date) - date) >= 2; "
        "delete from photo "
        "where extract(day from (SELECT NOW()::date) - date) >= 2; "
    )
    cursor.close()
    conn.commit()
    conn.close()
