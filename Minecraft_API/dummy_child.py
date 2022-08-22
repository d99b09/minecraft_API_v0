import asyncio

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import json
import time
import sys

from Mio_API_v02 import Mio_API

# mapi = Mio_API


def get_config(path):  # Получить конфиг из файла
    with open(path) as json_file:
        config = json.load(json_file)
    return config

# ****************************** ТВОЙ КОД НАЧИНАЕТСЯ ЗДЕСЬ! *******************************
class Worker(QRunnable):  # Это главный класс.
    def __init__(self):
        super().__init__()
        self.config_changed = False  # Стейт 1. Изменение конфигурации. Передается каждый раз, когда что-то меняется.
        self.stop_requested = False  # Стейт 2. Уничтожение процесса. Передается при закрытии окна.

    @pyqtSlot()
    def run(self):  # Здесь главный код. Именно он выполняется с самого начала одновременно с моим скриптом интерфейса.
        # print('Child process loop started!')
        # config = get_config('config.json')  # Получаем конфиг
        # print('Config obtained:')
        # print(config)

        # Что-то делаем
        # n = 0
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test(self))

        # while True:  # Главный луп
        #     if self.stop_requested:  # В начале каждой итерации проверка была ли отправлена команда на стоп.
        #         sys.exit()  # Если была, то убиваемся
        #     if self.config_changed:  # Теперь проверка на то был ли изменен конфиг
        #         print('Config changed, obtaining config again')
        #         config = get_config('config.json')  # Если был изменен, заново читаем файл, кладем конфиг в переменную
        #         self.config_changed = False  # ОБЯЗАТЕЛЬНО ПЕРЕКЛЮЧИТЬ ОБРАТНО!
        #         print(config)
        #
        #     # Выполняем тело лупа
        #     print(n)
        #     n += 1
        #     time.sleep(0.25)
# ****************************** ТВОЙ КОД ЗАКАНЧИВАЕТСЯ ЗДЕСЬ! *******************************

async def test(worker):
    print('Child process loop started!')
    config = get_config('config.json')  # Получаем конфиг
    print('Config obtained:')
    print(config)

    # Что-то делаем
    n = 0
    while True:
        while True:  # Главный луп
            if worker.stop_requested:  # В начале каждой итерации проверка была ли отправлена команда на стоп.
                sys.exit()  # Если была, то убиваемся
            if worker.config_changed:  # Теперь проверка на то был ли изменен конфиг
                print('Config changed, obtaining config again')
                config = get_config('config.json')  # Если был изменен, заново читаем файл, кладем конфиг в переменную
                worker.config_changed = False  # ОБЯЗАТЕЛЬНО ПЕРЕКЛЮЧИТЬ ОБРАТНО!
                print(config)
            print(n)
            n += 1
            await asyncio.sleep(0.25)

class Worker2:
    def __init__(self):
        self.config_changed = False  # Стейт 1. Изменение конфигурации. Передается каждый раз, когда что-то меняется.
        self.stop_requested = False  # Стейт 2. Уничтожение процесса. Передается при закрытии окна.

    async def test(self):
        print('Child process loop started!')
        config = get_config('config.json')  # Получаем конфиг
        print('Config obtained:')
        print(config)

        # Что-то делаем
        n = 0

        while True:  # Главный луп
            if self.stop_requested:  # В начале каждой итерации проверка была ли отправлена команда на стоп.
                sys.exit()  # Если была, то убиваемся
            if self.config_changed:  # Теперь проверка на то был ли изменен конфиг
                print('Config changed, obtaining config again')
                config = get_config(
                    'config.json')  # Если был изменен, заново читаем файл, кладем конфиг в переменную
                self.config_changed = False  # ОБЯЗАТЕЛЬНО ПЕРЕКЛЮЧИТЬ ОБРАТНО!
                print(config)
            print(n)
            n += 1
            await asyncio.sleep(0.25)

    async def test2(self):
        while True:
            print('Second thread')
            await asyncio.sleep(4)

    async def main_loop(self):
        asyncio.gather(test())


# Эта херня чисто для примера
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.counter = 0

        layout = QVBoxLayout()

        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        asyncio.get_event_loop()
        self.worker = Mio_API()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.threadpool.start(self.worker)


        b.pressed.connect(self.oh_no)

        layout.addWidget(self.l)
        layout.addWidget(b)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

    def oh_no(self):
        self.worker.config_changed = True

    def recurring_timer(self):
        self.counter += 1
        self.l.setText("Counter: %d" % self.counter)

    def closeEvent(self, *args, **kwargs):
        self.worker.stop_requested = True


app = QApplication([])
window = MainWindow()
test(window)
window.show()
sys.exit(app.exec())
