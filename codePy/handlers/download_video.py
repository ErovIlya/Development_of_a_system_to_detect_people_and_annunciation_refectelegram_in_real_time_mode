from codePy.telegram_bot.keyboard import (keyboard_after_download_video, keyboard_after_set_points, keyboard_cancel,
                                          keyboard_start, get_keyboard)
from codePy.yolo_model.info_about_video import get_first_frame, get_size_frame
from supervision import LineZone, Point
from codePy.telegram_bot.new_loop import create_new_loop_for_task
from codePy.telegram_bot.state_for_bot import Form
from codePy.telegram_bot.create_bot import bot
from aiogram.fsm.context import FSMContext
from aiogram import types, F, Dispatcher
from codePy.classes import StateForTask2
from aiogram.filters import Command
import datetime
import os


async def check_task(state: FSMContext) -> bool:
    _state = await state.get_state()
    return _state in [Form.start, Form.search, Form.download]


async def download_video_from_telegram(message: types.Message, state: FSMContext):
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    if not os.path.exists('../download'):
        os.mkdir('../download')
    if not os.path.exists('../download/video'):
        os.mkdir('../download/video')
    now_date = datetime.datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.datetime.now().strftime('%H-%M-%S')
    path = f"../download/video/{now_date}_{now_time}.mp4"
    await message.reply(text="Загрузка видео началась")
    await bot.download_file(file.file_path, path)

    data = {'path_video': path}
    await state.set_data(data)
    test_data = await state.get_data()
    print(test_data['path_video'])

    await message.reply(
        text=f"Видео успешно загрузилось.\nПуть к видеофайлу: {path}",
        reply_markup=keyboard_after_download_video
    )


async def set_points(message: types.Message, state: FSMContext):
    if await check_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    data = await state.get_data()
    path = data.get('path_video')
    if path is None:
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    width, height = get_size_frame(path)
    await bot.send_message(
        message.chat.id,
        text=f"Введите координаты точек через пробел\n"
             f"(Координаты должны быть в виде: X Y X Y)\n"
             f"Ширина:{width}; Высота: {height}",
        reply_markup=keyboard_cancel
    )
    await state.set_state(Form.point_state)


async def test_points(message: types.Message, state: FSMContext):
    if await check_task(state):
        await bot.send_message(message.chat.id, text="Запущена другая задача")
        return

    data = await state.get_data()
    path = data.get('path_video')
    if path is None:
        await message.reply(text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео")
        return

    points = message.text.split(" ")
    if len(points) == 4:
        try:
            x1 = int(points[0])
            y1 = int(points[1])
            x2 = int(points[2])
            y2 = int(points[3])
            width, height = get_size_frame(path)

            if not (0 <= x1 <= width and 0 <= x2 <= width and 0 <= y1 <= height and 0 <= y2 <= height):
                await message.reply("Введённые числа не подходят для данной задчи")
                return

            photo = types.FSInputFile(os.path.abspath(get_first_frame(path, [x1, y1], [x2, y2])))
            await state.set_state(Form.point_test)
            await bot.send_photo(message.chat.id, photo)

            line = LineZone(Point(x1, y1), Point(x2, y2))

            data['line'] = line
            await state.set_data(data)
            test_data = await state.get_data()
            print(test_data['line'])

            await message.reply(
                text="Если Вас всё устраивает, то нажмите кнопку 'Далее', если нет, то введите новые координаты точек",
                reply_markup=keyboard_after_set_points)
        except ValueError:
            await message.reply(
                "Неверный тип данных. Ожидались четыре целых число"
            )
            return
    else:
        await message.reply("Ожидались четыре целых число", reply_markup=keyboard_after_set_points)


async def start_task(message: types.Message, state: FSMContext):
    data = await state.get_data()
    path = data.get('path_video')
    if path is None or (await state.get_state() not in [Form.point_test, Form.point_test]):
        await message.reply(
            text="Для дальнейшего выполнения задачи необходимо, чтобы вы отправили видео",
            reply_markup=get_keyboard(await state.get_state())
        )
        return

    line = data.get('line')
    await create_new_loop_for_task(path, message.chat.id, StateForTask2.search(), line)

    await message.reply(text="Выполнение задачи началось", reply_markup=keyboard_start)
    await state.set_state(Form.search)


async def cancel(message: types.Message, state: FSMContext):
    _state = await state.get_state()
    if _state in [Form.point_state, Form.point_test]:
        await state.clear()
        await message.reply(text="Задача отменена", reply_markup=keyboard_start)


def download_video(dp: Dispatcher):
    dp.message.register(download_video_from_telegram, F.video)
    dp.message.register(set_points, Command(commands=['set_points']))
    dp.message.register(start_task, Command(commands=['next']), Form.point_test)
    dp.message.register(cancel, Command(commands=['cancel']))
    dp.message.register(test_points, Form.point_state)
    dp.message.register(test_points, Form.point_test)
