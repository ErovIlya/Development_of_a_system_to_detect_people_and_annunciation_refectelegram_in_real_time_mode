from codePy.yolo_model.info_about_video import get_first_frame_for_line, get_first_frame_for_zone, get_size_frame
from codePy.utils.classes_for_line_and_zone import WhichPointObjectBeTracked
from codePy.telegram_bot.keyboard import keyboard_set_sp_point
from codePy.utils.create_path_for_files import get_abs_path
from codePy.utils.loggind_file import log_info, log_error
from codePy.telegram_bot.state_for_bot import Form
from codePy.telegram_bot.create_bot import bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher
from aiogram.filters import Command
import codePy.utils.database as db


async def check_basic_task(state: FSMContext) -> bool:
    """
    ! Telegram: Проверка, что пользователь начал выполнять какое-либо основные задачи:
    поиск объектов в видео потоке (преобразование в видео или в реальном времени)
    :return: true - если задание от пользователя выполняется, false - нет
    """
    _state = await state.get_state()
    return _state in [Form.start, Form.search, Form.download]


async def check_additional_task(state: FSMContext) -> bool:
    """
    ! Telegram: Проверка, что пользователь начал выполнять какое-либо дополнительные задачи:
    установка точек для отрезка или зоны или определение "особой" точки
    :return: true - если задание от пользователя выполняется, false - нет
    """
    _state = await state.get_state()
    return _state in [Form.zone_state, Form.line_state, Form.point_state]


async def set_points_for_line(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/set_line]: Установка точек для линии пользователем
    """
    if await check_basic_task(state) or await check_additional_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    path = db.get_video_path(message.chat.id)
    if path is None:
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/set_line'")

    width, height = get_size_frame(path)
    await bot.send_message(
        message.chat.id,
        text=f"Введите координаты точек через пробел\n"
             f"(Координаты должны быть в виде: X Y X Y)\n"
             f"Ширина:{width}; Высота: {height}"
    )
    await state.set_state(Form.line_state)


async def test_points_for_line(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Проверка координат точек, введённых пользователем
    (отправка первого кадра с видео файла)
    """
    if await check_basic_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    path = db.get_video_path(message.chat.id)
    if path is None:
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) "
             f"пытается ввести координаты точек для отрезка")

    points = message.text.split(" ")
    if len(points) == 4:
        try:
            x1 = int(points[0])
            y1 = int(points[1])
            x2 = int(points[2])
            y2 = int(points[3])
            width, height = get_size_frame(path)

            if not (0 <= x1 <= width and 0 <= x2 <= width and 0 <= y1 <= height and 0 <= y2 <= height):
                await message.reply("Введённые числа не подходят для данной задачи")
                return

            photo = types.FSInputFile(get_abs_path(get_first_frame_for_line(path, [x1, y1], [x2, y2])))
            await state.set_state(Form.line_test)
            await bot.send_photo(message.chat.id, photo)

            point1 = db.insert_point(message.chat.id, x1, y1, 0)
            point2 = db.insert_point(message.chat.id, x2, y2, 0)

            log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл координаты точек для "
                     f"отрезка: x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")

            await message.reply(
                text="Если Вас всё устраивает, то нажмите кнопку 'Далее', если нет, то введите новые координаты точек"
            )
        except ValueError as e:
            log_error(e)

            await message.reply(
                "Неверный тип данных. Ожидались четыре целых число"
            )
            return
    else:
        await message.reply("Ожидались четыре целых число")


async def set_points_for_zone(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler [/set_zone]: Установка точек для зоны пользователем
    """
    if await check_basic_task(state) or await check_additional_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    path = db.get_video_path(message.chat.id)
    if path is None:
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл команду '/set_zone'")

    width, height = get_size_frame(path)
    await bot.send_message(
        message.chat.id,
        text=f"Введите координаты точек через точку с запятой (';') в нужной последовательности\n"
             f"Точек может быть от 3 до 5 штук включительно; В конце не должно быть точки с запятой (';')\n"
             f"(Координаты должны быть в виде: X Y;X Y; X Y)\n"
             f"Ширина видео:{width}; Высота видео: {height}"
    )
    await state.set_state(Form.zone_state)


async def test_points_for_zone(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Проверка координат точек, введённых пользователем
    (отправка первого кадра с видео файла)
    """
    if await check_basic_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    path = db.get_video_path(message.chat.id)
    if path is None:
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) "
             f"пытается ввести координаты точек для зоны")

    points = message.text.split(";")
    if not 3 <= len(points) <= 5:
        await message.reply("Ожидалось от 3 до 5 точек для зоны")
        return
    try:
        points_zone = []
        points_zone_coordinates = []
        for point in points:
            t_point = point.split(' ')
            x = int(t_point[0])
            y = int(t_point[1])
            width, height = get_size_frame(path)

            if not (0 <= x <= width and 0 <= y <= height):
                await message.reply(f"Введённые числа не подходят для данной задачи\n"
                                    f"(Ошибка связана с числами: {x} {y})")
                return
            point_id = db.insert_point(message.chat.id, x, y, 1)
            points_zone.append(point_id)
            points_zone_coordinates.append([x, y])
        db.insert_zone(message.chat.id, points_zone)

        photo = types.FSInputFile(
            get_abs_path(
                get_first_frame_for_zone(path, points_zone_coordinates)
            )
        )
        await state.set_state(Form.zone_test)
        await bot.send_photo(message.chat.id, photo)

        log_info(f"Пользователь {message.from_user.full_name} (ID = {message.chat.id}) ввёл координаты точек для "
                 f"зоны: {points_zone}")

        await message.reply(
            text="Если Вас всё устраивает, то нажмите кнопку 'Далее', если нет, то введите новые координаты точек"
        )
    except ValueError as e:
        log_error(e)

        await message.reply(
            "Перепроверьте введённые данные"
        )
        return


async def set_special_point(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Установка "особой" точки пользователем
    """
    if await check_basic_task(state) or await check_additional_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    if not db.check_video_file(message.chat.id):
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    await bot.send_message(
        message.chat.id, "Введите, по какой точке вы хотите, чтобы проходило отслеживание\n"
                         "(Наведите на значок 'клавиатуры' и выберите нужный вам вариант)",
        reply_markup=keyboard_set_sp_point
    )
    await state.set_state(Form.point_state)


async def test_special_point(message: types.Message, state: FSMContext) -> None:
    """
    ! Telegram handler: Проверка ввода "особой" точки (при неправильном вводе устанавливается вариант по умолчанию)
    """
    if not db.check_video_file(message.chat.id):
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    if message.text == "Центр нижнего ребра":
        db.insert_sp_point(message.chat.id, WhichPointObjectBeTracked.bottom_center())
        text = "Центр нижнего ребра"
    elif message.text == "Центр верхнего ребра":
        db.insert_sp_point(message.chat.id, WhichPointObjectBeTracked.up_center())
        text = "Центр верхнего ребра"
    elif message.text == "Центр правого ребра":
        db.insert_sp_point(message.chat.id, WhichPointObjectBeTracked.right_center())
        text = "Центр правого ребра"
    elif message.text == "Центр левого ребра":
        db.insert_sp_point(message.chat.id, WhichPointObjectBeTracked.left_center())
        text = "Центр левого ребра"
    else:
        db.insert_sp_point(message.chat.id, WhichPointObjectBeTracked.center())
        text = "Центр ограничивающей рамки"

    await state.clear()
    await message.reply(f"Точка '{text}' установлена", reply_markup=ReplyKeyboardRemove())


def set_points_for_video(dp: Dispatcher) -> None:
    dp.message.register(set_points_for_line, Command(commands=['set_line']))
    dp.message.register(set_points_for_zone, Command(commands=['set_zone']))
    dp.message.register(set_special_point, Command(commands=['set_point']))
    dp.message.register(test_points_for_line, Form.line_state)
    dp.message.register(test_points_for_line, Form.line_test)
    dp.message.register(test_points_for_zone, Form.zone_state)
    dp.message.register(test_points_for_zone, Form.zone_test)
    dp.message.register(test_special_point, Form.point_state)
