from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Controller2
import pyautogui

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
                              'ctrl': False, 'space': False}
        self.button_states = {'w': False, 'a': False, 's': False, 'd': False, 'e': False, 'shift': False,
                              'ctrl': False, 'space': False}

        self.button_headers = {}



    def run(self) -> None:
        while not self.is_done:
            self.mouse.move(self.x_speed, self.y_speed)
            self.keyboard_button_check_click()
            time.sleep(self.duration)

    def stop(self):
        self.is_done = True

    def rotationbyspeed(self, x, y):
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

            for e in self.pre_button_states:
                if self.pre_button_states[e] != self.button_states[e]:
                    if self.button_states[e]:
                        self.keyboard.press(e)
                    else:
                        self.keyboard.release(e)
            self.pre_button_states = self.button_states.copy()



def main():
    mapi = Minecraft_API_mio()
    # mapi.button_click()
    mapi.start()
    time.sleep(3)
    mapi.button_states['w'] = True
    # print(mapi.button_states)
    # print(mapi.pre_button_states)

    # mapi.rotationbyspeed(100, 100)
    time.sleep(5)
    print(mapi.pre_button_states)
    mapi.button_states['w'] = False
    print(mapi.button_states)
    print(mapi.pre_button_states)
    time.sleep(5)
    # mapi.button_states['w'] = True
    # time.sleep(5)
    # mapi.button_states['w'] = False

    mapi.stop()



if __name__ == '__main__':
    main()


