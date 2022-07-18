import asyncio
import json
import serial

import mqttools

from Minecraft_API.Minecraft_APi import Minecraft_API_mio

PORT = 1883
XY_LIMIT = 0.5
ROTATION_SPEED_INCREASE = 100


class Minecraft_client(Minecraft_API_mio):
    def __init__(self):
        super(Minecraft_client, self).__init__()
        self.json_channel_set = set()
        self.json_channel_list = [{'x': 0, 'y': 0, 's': 0}, {'x': 0, 'y': 0, 's': 0}]
        self.ser = serial.Serial()
        self.ser.port = '/dev/cu.usbserial-0001'
        self.ser.baudrate = 115200
        self.ser.timeout = 2
        self.ser.open()

    def bstr_to_intset(self, bstr):
        strset = set(bstr.decode())
        intset = set()
        for i in strset:
            try:
                intset.add(int(i))
            except:
                pass
        return intset

    async def start_client(self):
        client = mqttools.Client('localhost', PORT, connect_delays=[0.1])
        await client.start()
        return client

    def lv0(self, di, action_limit=0.5):
        action_bool = 0 if di['s'] < action_limit else 1
        return {'x': di['x'], 'y': di['y'], 'action': action_bool}

    async def left_band(self):
        client = await self.start_client()
        while True:
            topic = '/json_channel/' + str(self.json_channel_list[0])
            await client.subscribe(topic)
            message = client.messages.get()
            msg = json.loads(message.message.decode())
            msg_l0 = self.lv0(msg)
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
            if msg_l0 == 1:
                self.press_button('space')
            else:
                self.release_button('space')
            await asyncio.sleep(0.01)

    async def get_data(self):
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
            # print('Decode')
            # print(i_list)
            # print('JSON')
            if i_list[0]:
                x = -i_list[1]
            else:
                x = i_list[1]

            if i_list[2]:
                y = -i_list[3]
            else:
                y = i_list[4]
            #print(json.dumps({'x': x, 'y': y, 's': i_list[4]}))
            # # print(line.decode())
            await asyncio.sleep(0.05)


    async def right_band(self):
        client = await self.start_client()
        while True:
            # topic = '/json_channel/' + str(self.json_channel_list[1])
            # await client.subscribe(topic)
            # message = client.messages.get()

            msg = json.loads(message.message.decode())
            msg_l0 = self.lv0(msg)
            self.rotationbyspeed(msg_l0['x'] * ROTATION_SPEED_INCREASE, msg_l0['y'] * ROTATION_SPEED_INCREASE)
            if msg_l0 == 1:
                self.press_button('i')
            else:
                self.release_button('i')

            await asyncio.sleep(0.01)






    async def get_channels(self):
        client = await self.start_client()
        while True:
            await client.subscribe('/open_channels')
            message = await client.messages.get()
            print(f'Message: {message.message}')
            self.json_channel_set = self.bstr_to_intset(message.message)
            print(f'Devise number: {self.json_channel_set}')
            self.json_channel_list = list(self.json_channel_set)

            await asyncio.sleep(1)

    # async def get_jsons(self):
    #     print('Get json start')
    #     client = await self.start_client()
    #     while True:
    #         # print(self.json_channels_set)
    #         try:
    #             topic = '/json_channel/' + str(device_number)
    #             await client.subscribe(topic)
    #             message = await asyncio.wait_for(client.messages.get(), timeout=7.5)
    #             msg = json.loads(message.message.decode())
    #             print('Message json:')
    #             print(msg)
    #             print('Lv0')
    #             msg_l0 = self.lv0(msg)
    #             print(msg_l0)
    #         except:
    #             break
    #         await asyncio.sleep(1)

    async def client_main(self):
        await asyncio.gather(
            self.run(),
            self.left_band(),
            self.right_band(),
        )

