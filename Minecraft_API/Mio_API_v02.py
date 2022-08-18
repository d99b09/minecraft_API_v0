import os
import argparse
from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Controller2
from pynput.keyboard import Key
import asyncio
import serial
import time
import json

class Mio_API:
    def __init__(self):
        self.armbands_by_id = dict()
        self.json_data_from_serial = dict()
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
        # self.ser.open()
        self.json_init()



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

    def json_init(self):
        with open('config.json', mode='r') as f:
            self.json_config = json.load(f)
        for armband in self.json_config['armbands']:
            self.json_data_from_serial[armband['id']] = {'x': 0, 'y': 0, 's': 0}
            self.armbands_by_id[armband['id']] = armband
        print(self.json_data_from_serial)
        print(self.armbands_by_id)
        for i in self.armbands_by_id:
            print(i)

    async def get_data_from_serial_by_id(self):#TODO
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
            s = i_list[4]

            for armband_id in self.armbands_by_id:
                if armband_id == i_list[5]:
                    self.json_data_from_serial[armband_id] = {'x': x, 'y': y, 's': s}
            print(self.json_data_from_serial)

            # print(self.json_data_band1, '                 ', self.json_data_band2)

            await asyncio.sleep(0.05)

    async def controller_mouse_with_config(self):
        while True:

            await asyncio.sleep(0.05)

    async def controller_keyboard_with_config(self):
        while True:

            await asyncio.sleep(0.05)





if __name__ == '__main__':
    mapi = Mio_API()
    mapi.json_init()

