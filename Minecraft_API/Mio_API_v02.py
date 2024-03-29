import json
import os
import sys

from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Controller2
from pynput.keyboard import Key
import asyncio
import serial
import time
from PyQt6.QtCore import QRunnable, pyqtSlot

ROTATION_SPEED_INCREASE = 50
XY_LIMIT = 3

class Mio_API(QRunnable):
    def __init__(self, mode=0):
        super().__init__()
        self.sleep_time = 0
        self.config_changed = False
        self.stop_requested = False
        self.mode = mode
        self.mouse = Controller()
        self.keyboard = Controller2()
        self.start_time = time.time()
        self.x_speed, self.y_speed = 0, 0
        self.duration = 1
        self.is_done = False
        self.pre_button_states = {'w': False, 'a': False, 's': False, 'd': False, 'e': False, 'shift': False,
                                  'ctrl': False, 'space': False, 'left_click': False, 'right_click': False}
        self.button_states = {'w': False, 'a': False, 's': False, 'd': False, 'e': False, 'shift': False,
                              'ctrl': False, 'space': False, 'left_click': False, 'right_click': False}

        self.button_keyboard_headers = {'w': 'w', 'a': 'a', 's': 's', 'd': 'd', 'e': 'e', 'shift': Key.shift,
                                        'ctrl': Key.ctrl, 'space': Key.space}
        self.button_mouse_headers = {'left_click': Button.left, 'right_click': Button.right}
        self.ser = serial.Serial()
        self.ser.port = 'COM3'
        self.ser.baudrate = 115200
        self.ser.timeout = 2
        self.is_open = False
        self.json_data_with_config = dict()
        self.my_json_config = dict()
        self.init_json()

    @pyqtSlot()
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.main_loop())

    def minecraft_launcher_launch(self):
        os.system("open /Users/dima/Downloads/TLauncher-2.86/TLauncher-2.86.jar")#mac os

    async def open_serial(self):
        while True:
            # print(self.is_open)
            try:
                self.ser.open()
                line = self.ser.readline()
                self.is_open = True
                # print(self.is_open)
                break
            except:
                self.is_open = False
            await asyncio.sleep(3)

    async def mouse_run(self) -> None:
        while not self.is_done:
            # print(self.x_speed, self.y_speed)
            self.mouse.move(self.x_speed, self.y_speed)
            self.keyboard_button_check_click()
            await asyncio.sleep(self.duration)
            # await asyncio.sleep(1)

    def stop(self):
        self.is_done = True

    def rotationbyspeed(self, x, y):
        # print('rotation')
        if x != 0 and y != 0:
            min_speed = min(abs(x), abs(y))
        elif x != 0:
            min_speed = abs(x)
        elif y != 0:
            min_speed = abs(y)
        else:
            min_speed = 1
        self.x_speed = x/min_speed
        self.y_speed = y/min_speed
        self.duration = 1/min_speed

    def keyboard_button_check_click(self):#TODO redesign
        if self.pre_button_states != self.button_states:
            print(self.pre_button_states)
            for e in self.pre_button_states:
                if self.pre_button_states[e] != self.button_states[e]:
                    if self.button_states[e]:
                        if e in self.button_mouse_headers:
                            self.mouse.press(self.button_mouse_headers[e])
                        else:
                            self.keyboard.press(self.button_keyboard_headers[e])
                    else:
                        if e in self.button_mouse_headers:
                            self.mouse.release(self.button_mouse_headers[e])
                        else:
                            self.keyboard.release(self.button_keyboard_headers[e])
            self.pre_button_states = self.button_states.copy()
            print(self.pre_button_states)

    def press_button(self, button):
        self.button_states[button] = True

    def release_button(self, button):
        self.button_states[button] = False

    def press_gesture_mouse_button(self, button):
        self.mouse.press(self.button_mouse_headers[button])
        self.mouse.release(self.button_mouse_headers[button])

    def init_json(self):
        with open('config.json', mode='r') as f:
            self.json_config = json.load(f)
        # print(self.json_config)
        self.armbands = self.json_config['armbands']
        for armband in self.armbands:
            self.json_data_with_config[armband["id"]] = {'x': 0, 'y': 0, 's': 0}
            self.my_json_config[armband["id"]] = armband
            if armband["arm"] == "right":
                self.right_id = armband["id"]
            elif armband["arm"] == "left":
                self.left_id = armband["id"]
        # print(self.my_json_config)

    async def get_data_with_config(self):
        while True:
            # print(self.is_open)
            while self.is_open:
                print('Data:')
                line = self.ser.readline()
                print(line)
                s_list = line.decode().split(',')[:-1]
                i_list = []
                for i in s_list:
                    try:
                        i_list.append(int(i))
                    except:
                        pass
                try:
                    if i_list[0]:
                        x = -i_list[1]
                    else:
                        x = i_list[1]

                    if i_list[2]:
                        y = -i_list[3]
                    else:
                        y = i_list[3]

                    s = i_list[4]
                    band_id = str(i_list[5])
                    self.json_data_with_config[band_id] = {'x': -y, 'y': x, 's': s}
                    print(self.json_data_with_config)
                except:
                    pass
                await asyncio.sleep(self.sleep_time)
            await asyncio.sleep(0.1)

    async def controller_with_config(self):
        while True:
            pass

    async def controller_right_band_with_config(self):

        while self.my_json_config[self.right_id]["enabled"]:
            msg_l0 = self.json_data_with_config[self.right_id]
            if self.my_json_config[self.right_id]["mode"] == "mouse":
                self.rotationbyspeed(msg_l0['x'] * ROTATION_SPEED_INCREASE, msg_l0['y'] * ROTATION_SPEED_INCREASE)
                if msg_l0['s'] == 1:
                    self.press_button(self.my_json_config[self.right_id]["bindings"]["gesture_1"])
                else:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["gesture_1"])

            elif self.my_json_config[self.right_id]["mode"] == "hotkeys":
                if msg_l0['x'] > XY_LIMIT:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_left"])
                    self.press_button(self.my_json_config[self.right_id]["bindings"]["tilt_right"])
                elif msg_l0['x'] < -XY_LIMIT:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_right"])
                    self.press_button(self.my_json_config[self.right_id]["bindings"]["tilt_left"])
                else:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_right"])
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_left"])
                if msg_l0['y'] > XY_LIMIT:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_backward"])
                    self.press_button(self.my_json_config[self.right_id]["bindings"]["tilt_forward"])
                elif msg_l0['y'] < -XY_LIMIT:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_forward"])
                    self.press_button(self.my_json_config[self.right_id]["bindings"]["tilt_backward"])
                else:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_forward"])
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["tilt_backward"])
                if msg_l0['s'] == 1:
                    self.press_gesture_mouse_button(self.my_json_config[self.right_id]["bindings"]["gesture_1"])
                else:
                    self.release_button(self.my_json_config[self.right_id]["bindings"]["gesture_1"])
            await asyncio.sleep(self.sleep_time)

    async def controller_left_band_with_config(self):
        while self.my_json_config[self.left_id]["enabled"]:
            print(self.my_json_config[self.left_id]["mode"])
            msg_l0 = self.json_data_with_config[self.left_id]
            if self.my_json_config[self.left_id]["mode"] == "mouse":
                self.rotationbyspeed(msg_l0['x'] * ROTATION_SPEED_INCREASE, msg_l0['y'] * ROTATION_SPEED_INCREASE)
                if msg_l0['s'] == 1:
                    self.press_gesture_mouse_button(self.my_json_config[self.left_id]["bindings"]["gesture_1"])
                else:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["gesture_1"])

            elif self.my_json_config[self.left_id]["mode"] == "hotkeys":
                print(msg_l0)
                print(msg_l0['x'])
                if msg_l0['x'] > XY_LIMIT:
                    print(1111111)
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_left"])
                    self.press_button(self.my_json_config[self.left_id]["bindings"]["tilt_right"])
                elif msg_l0['x'] < -XY_LIMIT:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_right"])
                    self.press_button(self.my_json_config[self.left_id]["bindings"]["tilt_left"])
                else:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_right"])
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_left"])
                if msg_l0['y'] > XY_LIMIT:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_backward"])
                    self.press_button(self.my_json_config[self.left_id]["bindings"]["tilt_forward"])
                elif msg_l0['y'] < -XY_LIMIT:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_forward"])
                    self.press_button(self.my_json_config[self.left_id]["bindings"]["tilt_backward"])
                else:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_forward"])
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["tilt_backward"])
                if msg_l0['s'] == 1:
                    self.press_button(self.my_json_config[self.left_id]["bindings"]["gesture_1"])
                else:
                    self.release_button(self.my_json_config[self.left_id]["bindings"]["gesture_1"])
            await asyncio.sleep(self.sleep_time)

    async def check_button_now(self):
        while 1:
            for state in self.button_states:
                if self.button_states[state]:
                    print(state)
            await asyncio.sleep(self.sleep_time)

    async def check_config(self):
        while True:

            if self.stop_requested:  # В начале каждой итерации проверка была ли отправлена команда на стоп.
                sys.exit()  # Если была, то убиваемся
            if self.config_changed:  # Теперь проверка на то был ли изменен конфиг
                print('Config changed, obtaining config again')
                self.init_json()
                self.config_changed = False  # ОБЯЗАТЕЛЬНО ПЕРЕКЛЮЧИТЬ ОБРАТНО!
                print(self.my_json_config)
            await asyncio.sleep(1)

    async def main_loop(self):

        await asyncio.gather(
            self.mouse_run(),
            self.check_config(),
            self.check_button_now(),
            self.get_data_with_config(),
            self.controller_left_band_with_config(),
            # self.controller_right_band_with_config(),
            self.open_serial()

        )


if __name__ == '__main__':
    mapi = Mio_API()
    mapi.init_json()
    asyncio.run(mapi.main_loop())