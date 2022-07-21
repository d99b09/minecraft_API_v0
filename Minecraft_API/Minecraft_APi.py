import os

from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Controller2
from pynput.keyboard import Key
import asyncio
import serial
import time
from threading import Thread


ROTATION_SPEED_INCREASE = 50
XY_LIMIT = 3


class Minecraft_API_mio():
    def __init__(self):
        self.mouse = Controller()
        self.keyboard = Controller2()
        self.start_time = time.time()
        self.x_speed, self.y_speed = 0, 0
        self.duration = 0.001
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
        print('rotation')
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

    async def get_data(self):
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

    async def controller(self):
        while True:
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

    async def control_loop(self):
        await asyncio.gather(
            self.run(),
            self.get_data(),
            self.controller()
        )




mapi = Minecraft_API_mio()

async def controller():
    while 1:
        await asyncio.sleep(3)
        mapi.rotationbyspeed(100, 100)
        await asyncio.sleep(3)

        mapi.rotationbyspeed(300, 300)
        await asyncio.sleep(3)
        mapi.release_button('w')
        mapi.release_button('w')


async def main():
   await asyncio.gather(
       # controller(),
       mapi.run()
   )


if __name__ == '__main__':
    mapi = Minecraft_API_mio()
    asyncio.run(mapi.control_loop())
    # mapi.minecraft_launcher_launch()

