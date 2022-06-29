from threading import Thread
import random

class demo_publishe(Thread):

    def get_random_x(self):
        return random.uniform(-1, 1)

    def get_random_y(self):
        return random.uniform(-1, 1)

    def random_r(self):
        return random.randint(0, 2)

    def random_finger_action(self):
        return random.randint(0, 2)

    def random_palm_action(self):
        return random.randint(0, 2)

    def random_finger_state(self):
        return random.choice([True, False])

    def random_palm_state(self):
        return random.choice([True, False])

    def random_r_state(self):
        return random.choice([True, False])

    def get_random_JSON(self):
        pass


if __name__ == '__main__':
    for _ in range(10):
        print(random.choice([True, False]))






