# Разработка системы по обнаружению людей и оповещению через Telegram в режиме реального времени

> Программа разработана в обучающих целях в качестве курсовой работы


Программа представляет собой связь телеграмм-бота библиотеки `aiogram` и модели нейронной сети глубокого обучения и компьютерного зрения `YOLO` (в частности `YOLOv8`)


 
[Ссылка на файлы по умолчанию](https://cloud.mail.ru/public/QdyA/Z7qgAvxpf) (вместо предложенного видео файла и фотографии можно вставить свои)</br>

------------------------------

## Необходимые компоненты для работы программы

* `Visual Studio 2017/2019`
* Необходимые компоненты `Visual Studio 2017/2019` (некоторые из них, может быть, и не нужны вовсе):
  - Инструменты `Visual C++` для `CMake`
  - Средства профилирования `C++`
  - `Visual C++ ATL` для `x86` и `x64`
  - `VC++ 2017 version 15.9 v14.16 latest v141`
* [`Visuaul Studio Build Tools 2022`](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
* `python 3.9` (новее не подойдут)
* `CUDA` (11.8 или 12.1) и `CuDNN`
* библиотека `torch` (для генерации установочного кода перейдите по [ссылке](https://pytorch.org/get-started/locally/))
> При установке могут возникнуть проблемы с `YOLO`, в частности с установкой библиотеки `lap` и/или с производительностью (один кадр будет обрабатываться около 200-400 мс). Поэтому и появились данные требования

--------------------------
### Порядок работы пользователя с телеграмм ботом: 
+ Стандартная задача детектирования людей
  + ~~_Видео файл &#8594; Поток_~~
    + ~~Команда `/stream1` для запуска обработки~~
    + ~~Команда `/stop` для остановки обработки~~
    + ~~Команда `/status` для получения промежуточных итогов~~
  + _Видео файл &#8594; Видео файл_
    + Команда `/task1` для запуска обработки
  > Если пользователь не отправлял видео файл ранее, то будет происходить поиск в видео файле `video_task_1.mkv`
+ Задача детектирования людей, которые входят в зону поиска, и подсчета прохождения через отрезок
  + ~~_Видео файл &#8594; Поток_~~
    + ~~Команда `/stream2` для запуска обработки~~
    + ~~Команда `/stop` для остановки обработки~~
    + ~~Команда `/status` для получения промежуточных итогов~~
  + _Видео файл &#8594; Видео файл_
    + Команда `/task2` для запуска обработки
  > - Если пользователь не отправлял видео файл ранее, то будет происходить поиск в видео файле `video_task_2.mkv`
  > - Если пользователь не определял точки для зоны поиска, то детектирование будет проходить на всём кадре
  > - Если пользователь не определял точки для отрезка подсчета прохождения, то он будет автоматически построен по диагонали кадра
  > - Если пользователь не определял точку, по которой будет проходить детектирование каждого объекта, то она будет по умолчанию соответствовать середине прямоугольника обнаруженного объекта
+ Создание пользовательской задачи
  + _Видео файл &#8594; Видео файл_
    + Команда `/download`: скачивание выбранного видео файла из облака `Mail`
    > - После ввода команды бот отправит ссылку на облако, куда необходимо выгрузить видео файл
    > - После успешной загрузки файла на облако боту необходимо написать название файла с расширением
    > - Бот продолжит работу только в том случае, если файл успешно скачан и имеет расширение `.mkv` или `.mp4`
    + Команда `/set_zone`: после этой команды пользователю предложат ввести координаты точек для зоны, в которой будут детектироваться объекты
    > - Минимальное количество точек равно 3, максимальное - 5
    > - Координаты точек вводятся по шаблону: `X Y;X Y;X Y;X Y;X Y`
    + Команда `/set_line`: после этой команды пользователю предложат ввести координаты точек для отрезка, прохождение через которого будет вестись подсчет
    > Координаты точек вводятся по шаблону: `X Y X Y`
    + Команда `/set_point`: после этой команды пользователю предложат выбрать "особую" точку, по которой будет ввестись детектирование
    > - После ввода команды появится клавиатура с доступными вариантами
    > - Если пользователь введёт что-то иное, кроме доступных вариантов, то по умолчанию будет выбран вариант точки, которая соответствует середине прямоугольника обнаруженного объекта
    + Команда `/next`: запуск пользовательской задачи после установки точек для зоны и отрезка
    + Команда `/cancel`: отмена текущего ввода данных
+ Другие команды
  + Команда `/hi`: приветствие с пользователем
  + Команда `/system`: информация об операционной системе, `CUDA` и `CuDNN`
  + Команда `/clear`: очистка сервера, облака от файлов, скачанных и выгруженных более 2 дней назад
  + Команда `/info`: краткая информация о боте
  + Команда `/photo`: отправление последней скачанной от пользователя фотографии с обнаруженными объектами
    
--------------------------

### Список изменений в соответствии с commit (почти): 
- Создание проекта (курсовая работа)
  - Создание телеграмм бота
  - Создание функций для задачи детектирования объектов (людей) на видео файле/веб камере и оповещению при обнаружении нового объекта
  - Выделение отдельного потока для данной задачи
- Исправление и доработка
  - Переход с `aiogram 2` на `aiogram 3`
  - Доработка различных классов и методов
  - Добавление `required.txt`, `.gitignore`
- Добавление задачи подсчета количества объектов, пересекающих отрезок
  - Доработка телеграмм бота для запуска задачи
  - Создание функций для решения задач
  - Рефакторинг кода
- Улучшение задачи подсчета количества объектов, пересекающих отрезок
  - Исправление алгоритма
  - Добавление зоны обнаружения объектов и ключевой точки, по которой происходит детектирование
  - Добавление таймера для объектов, показывающих, сколько секунд они находятся в зоне
  - Добавление обработки видео файла в видео файл (*"Видео &#8594; Видео"*)
  - Добавление скачивания, выгрузки файлов в `Cloud Mail.ru`
- Исправление и доработка
  - Убрана задача *"Видео &#8594; Поток"* (файлы остались, но запустить данную задачу пользователь не может)
  - Убрана клавиатура для быстрого набора команд
  - Добавлена БД PostgreSQL для удобного хранения относительных путей, точек, отрезок и зон, созданных пользователем
- Исправление багов

#### Небольшие уточнения:
Для работы с `Cloud Mail.ru` используется библиотека `webdavclient`.
Из-за её ограничений на облаке невозможно создавать/удалять несколько директорий за короткий промежуток
времени.
