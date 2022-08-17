import os
import argparse
from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Controller2
from pynput.keyboard import Key
import asyncio
import serial
import time
import json



ROTATION_SPEED_INCREASE = 50
XY_LIMIT = 3

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("--a")

class Minecraft_API_mio():
    def __init__(self, mode=0):
        self.mode = mode
        self.mouse = Controller()
        self.keyboard = Controller2()
        self.start_time = time.time()
        self.x_speed, self.y_speed = 0, 0
        self.duration = 1
        self.is_done = False
        self.pre_button_states = {'w': False, 'a': False, 's': False, 'd': False, 'e': False, 'shift': False,
                              'ctrl': False, 'space': False, 'lCkick': False, 'rClick': False}
        self.button_states = {'w': False, 'a': False, 's': False, 'd': False, 'e': False, 'shift': False,
                              'ctrl': False, 'space': False, 'lCkick': False, 'rClick': False}

        self.button_keyboard_headers = {'w': 'w', 'a': 'a', 's': 's', 'd': 'd', 'e': 'e', 'shift': Key.shift,
                                        'ctrl': Key.ctrl, 'space': Key.space}
        self.button_mouse_headers = {'lCkick': Button.left, 'rClick': Button.right}
        self.ser = serial.Serial()
        self.ser.port = '/dev/cu.usbserial-0001'
        self.ser.baudrate = 115200
        self.ser.timeout = 2
        self.ser.open()
        self.json_data = {'x': 0, 'y': 0, 's': 0}
        self.json_data_band1 = {'x': 0, 'y': 0, 's': 0}
        self.json_data_band2 = {'x': 0, 'y': 0, 's': 0}




    def minecraft_launcher_launch(self):
        os.system("open /Users/dima/Downloads/TLauncher-2.86/TLauncher-2.86.jar")#mac os


    async def run(self) -> None:
        while not self.is_done:
            print(self.x_speed, self.y_speed)
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

    def keyboard_button_check_click(self):

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

    async def get_test_data(self):
        while True:
            line = self.ser.readline()
            # print(line)
            await asyncio.sleep(3)
            line1 = 0
            line2 = 0
            while 1:
                line = self.ser.readline()
                # print(line)
                s_list = line.decode().split(',')[:-1]
                i_list = []

                for i in s_list:
                    try:
                        i_list.append(int(i))
                    except:
                        pass
                if len(i_list) == 0:
                    await asyncio.sleep(1)
                    continue

                if i_list[-1] == 1:
                    line1 = line
                else:
                    line2 = line
                print(line1, '                 ', line2)
                await asyncio.sleep(0.1)

    async def get_data_one_band(self):
        line = self.ser.readline()
        await asyncio.sleep(3)

        while 1:
            line = self.ser.readline()
            print(line)
            s_list = line.decode().split(',')[:-1]
            i_list = []
            for i in s_list:
                try:
                    i_list.append(int(i))
                except:
                    pass
            if len(i_list) == 0:
                await asyncio.sleep(1)
                continue
            if i_list[0]:
                x = -i_list[1]
            else:
                x = i_list[1]

            if i_list[2]:
                y = -i_list[3]
            else:
                y = i_list[3]
            self.json_data = {'y': x, 'x': y, 's': i_list[4]}
            print(self.json_data)
            await asyncio.sleep(0.05)

    async def get_data_two_band(self):
        line = self.ser.readline()
        await asyncio.sleep(3)

        while 1:
            line = self.ser.readline()
            # print(line)
            s_list = line.decode().split(',')[:-1]
            i_list = []
            for i in s_list:
                try:
                    i_list.append(int(i))
                except:
                    pass
            if i_list[0]:
                x = -i_list[1]
            else:
                x = i_list[1]

            if i_list[2]:
                y = -i_list[3]
            else:
                y = i_list[3]
            if i_list[4] == 1:#???
                self.json_data_band1 = {'x': x, 'y': y, 's': i_list[4]}
            if i_list[4] == 2:
                self.json_data_band2 = {'x': x, 'y': y, 's': i_list[4]}
            print(self.json_data_band1, '                 ', self.json_data_band2)

            await asyncio.sleep(0.05)

    async def controller_minecraft_one_band_v1(self):
        while True:#self.mode == 'mine':
            if self.json_data['s']:
                self.rotationbyspeed(self.json_data['x'] * ROTATION_SPEED_INCREASE,
                                     self.json_data['y'] * ROTATION_SPEED_INCREASE)
            else:
                if self.json_data['x'] > XY_LIMIT:
                    self.release_button('a')
                    self.press_button('d')
                elif self.json_data['x'] < -XY_LIMIT:
                    self.release_button('d')
                    self.press_button('a')
                else:
                    self.release_button('d')
                    self.release_button('a')
                if self.json_data['y'] > XY_LIMIT:
                    self.release_button('s')
                    self.press_button('w')
                elif self.json_data['y'] < -XY_LIMIT:
                    self.release_button('w')
                    self.press_button('s')
                else:
                    self.release_button('w')
                    self.release_button('s')

            await asyncio.sleep(0.05)

    async def controller_minecraft_one_band_v2(self):
        while True:
            if self.json_data['y'] > XY_LIMIT:
                self.release_button('s')
                self.press_button('w')
            elif self.json_data['y'] < -XY_LIMIT:
                self.release_button('w')
                self.press_button('s')
            else:
                self.release_button('w')
                self.release_button('s')
            if abs(self.json_data['x']) > 2:
                self.rotationbyspeed(self.json_data['x'] * ROTATION_SPEED_INCREASE,
                                     0)

    async def controller_minecraft_two_band_v1(self):
        while True:
            msg_l0 = self.json_data_band1
            if msg_l0['x'] > XY_LIMIT:
                self.release_button('a')
                self.press_button('d')
            elif msg_l0['x'] < -XY_LIMIT:
                self.release_button('d')
                self.press_button('a')
            else:
                self.release_button('d')
                self.release_button('a')
            if msg_l0['y'] > XY_LIMIT:
                self.release_button('s')
                self.press_button('w')
            elif msg_l0['y'] < -XY_LIMIT:
                self.release_button('w')
                self.press_button('s')
            else:
                self.release_button('w')
                self.release_button('s')
            if msg_l0['s'] == 1:
                self.press_button('space')
            else:
                self.release_button('space')
            msg_r = self.json_data_band2
            self.rotationbyspeed(msg_r['x'] * ROTATION_SPEED_INCREASE, msg_r['y'] * ROTATION_SPEED_INCREASE)
            if msg_r == 1:
                self.press_button('i')
            else:
                self.release_button('i')
            await asyncio.sleep(0.01)

    async def controller_mouse(self):
        while True: #self.mode == 'mouse':
            self.rotationbyspeed(self.json_data['x'] * ROTATION_SPEED_INCREASE,
                                 self.json_data['y'] * ROTATION_SPEED_INCREASE)
            if self.json_data['s']:
                self.mouse.press(Button.left)
                self.mouse.release(Button.left)
            await asyncio.sleep(0.01)

    async def upload_code(self):
        while True:
            a = input()
            print(type(a))
            print(a)

    async def control_loop(self):

        await asyncio.gather(
            # self.run(),
            self.get_data_one_band(),
            # self.get_data_two_band(),

            # self.get_test_data(),
            # self.controller_minecraft_one_band_v1(),
            # self.controller_minecraft_one_band_v2(),
            # self.controller_mouse(),
            # self.upload_code()
        )



if __name__ == '__main__':
    # args = parser.parse_args()
    # a = args.a
    mapi = Minecraft_API_mio()
    asyncio.run(mapi.control_loop())
    # mapi.minecraft_launcher_launch()

