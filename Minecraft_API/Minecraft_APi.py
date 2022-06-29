import os

from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Controller2
from pynput.keyboard import Key
import asyncio

import time
from threading import Thread

class Minecraft_API_mio(Thread):
    def __init__(self):
        super().__init__()
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

    def minecraft_launcher_launch(self):
        os.system("open /Users/dima/Downloads/TLauncher-2.86/TLauncher-2.86.jar")#mac os


    def run(self) -> None:
        while not self.is_done:
            # print(self.x_speed, self.y_speed)
            self.mouse.move(self.x_speed, self.y_speed)
            self.keyboard_button_check_click()
            time.sleep(self.duration)
            #time.sleep(0.1)

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






def main():
    mapi = Minecraft_API_mio()
    mapi.minecraft_launcher_launch()
    return 0
    # mapi.button_click()
    mapi.start()
    time.sleep(3)
    mapi.press_button('w')
    # mapi.button_states['w'] = True
    # print(mapi.button_states)
    # print(mapi.pre_button_states)

    #mapi.rotationbyspeed(100, 100)
    # time.sleep(5)
    # print(mapi.pre_button_states)
    # mapi.button_states['w'] = False
    # print(mapi.button_states)w
    # print(mapi.pre_button_states)
    time.sleep(5)
    mapi.release_button('w')
    print(mapi.pre_button_states)
    print(mapi.button_states)
    time.sleep(1)

    # mapi.button_states['w'] = True
    # time.sleep(5)
    mapi.button_states['w'] = False

    mapi.stop()



if __name__ == '__main__':
    main()


