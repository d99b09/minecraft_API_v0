import pynput
import time

time.sleep(5)
mouse = pynput.mouse.Controller()
mouse.move(10, 10)

def move_smooth(xm, ym, t):
    for i in range(t):
        if i < t/2:
            h = i
        else:
            h = t - i
        mouse.move(h*xm, h*ym)
        time.sleep(1/60)

move_smooth(2, 2, 40)