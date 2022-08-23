import time
from threading import Thread
from pynput.mouse import Button, Controller
import serial

from Minecraft_API.constants import SERIAL_PORT


class Mio_API_mouse(Thread):
    def __init__(self):
        super(Mio_API_mouse, self).__init__()
        self.s = False
        self.duration = 1
        self.y_speed = 0
        self.x_speed = 0
        self.mouse = Controller()
        self.button_mouse_headers = {'left_click': Button.left, 'right_click': Button.right}
        self.button_states = {'left_click': False, 'right_click': False}
        self.pre_button_states = {'left_click': False, 'right_click': False}

    def run(self):
        while True:

            self.mouse.move(self.x_speed, self.y_speed)
            self.button_check(self.s, 'left_click')
            time.sleep(self.duration)

    def button_check(self, s, button_name):
        if s:
            if not self.pre_button_states[button_name]:
                self.mouse.press(self.button_mouse_headers[button_name])
                self.pre_button_states[button_name] = True
        else:
            if self.pre_button_states[button_name]:
                self.mouse.release(self.button_mouse_headers[button_name])
                self.pre_button_states[button_name] = False

    def rotationbyspeed(self, x, y):
        print('rotation')
        print(x, y)
        if x != 0 and y != 0:
            min_speed = min(abs(x), abs(y))
        elif x != 0:
        elif y != 0:
            min_speed = abs(y)
        else:
            min_speed = 1
        self.x_speed = x / min_speed
        self.y_speed = y / min_speed
        self.duration = 1 / min_speed
        # if x != 0 or y != 0:
        #     self.duration = 0.001
        #     self.x_speed = x * self.duration
        #     self.y_speed = y * self.duration
        # else:
        #     self.x_speed = 0
        #     self.y_speed = 0


class Mio_API_get_data(Thread):
    def __init__(self, mouse_control):
        super(Mio_API_get_data, self).__init__()
        self.mouse_control = mouse_control
        self.json_data_with_config = dict()
        self.ser = serial.Serial()
        self.ser.port = SERIAL_PORT
        self.ser.baudrate = 115200
        self.ser.timeout = 2

    def run(self):
        self.open_serial()

    def open_serial(self):
        while True:
            try:
                print('Trying to open port')
                self.ser.open()
                line = self.ser.readline()
                print(f'Data: {line}')
                while True:
                    line = self.ser.readline()
                    print(f'Data: {line}')
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

                    except:
                        pass

            except:
                time.sleep(3)
                self.ser.close()


if __name__ == '__main__':
    mouse_control = Mio_API_mouse()
    get_data = Mio_API_get_data(mouse_control=mouse_control)
    get_data.start()



