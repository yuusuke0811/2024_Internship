# -*- coding: utf-8 -*-

from Common.common import read_file
from Common.logger import Logger
from Common.Constant.common import MAX_DIVISION_NUMBER
from Common.Constant.transmission_type import CONECT, STREAMING
from Common.Constant.client_type import CAMERA

import websockets
import cv2
import json
import base64
import time
import math
import subprocess
import re
import datetime
import socket  

class Client(Logger):
    ''' Websocketクライアントクラス '''

    def __init__(self, log_level: int):
        ''' コンストラクタ
        
        :param int log_level: ログレベル
        '''
        super().__init__(log_level, 'WebsocketClient.log')

    def initialize(self):
        ''' 初期化処理 '''

        # 設定ファイルを読み込み
        conf = read_file('clientConfig.json')

        # ネットワーク内に接続している機器の死活チェック
        subprocess.run('./Common/NetworkAliveCheck.sh', stdout=subprocess.DEVNULL)

        # 同一ネットワーク内のarp情報を取得
        sp_arp = subprocess.Popen(['arp', '-a'], encoding='utf-8', stdout=subprocess.PIPE)
        sp_grep = subprocess.Popen(['grep', conf['server_mac_addr']], stdin=sp_arp.stdout, encoding='utf-8', stdout=subprocess.PIPE)
        sp_arp.stdout.close()
        out, err = sp_grep.communicate()
            
        if out == '':
            raise Exception('接続先のサーバが見つかりません。')
        
        ip_addr = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', out)[0]
        
        self.url = f'ws://{ ip_addr }:{ conf["port"] }'
        self.capacity = conf['capacity']
        self.capture = cv2.VideoCapture(conf['camera'])

        self.id = -1

    async def send_conect_info(self, websocket, json_data):
        ''' 接続情報送信 '''

        self.logger.info(json_data['message'])

        self.id = json_data['id']
        
        json_data['clientType'] = CAMERA
        json_data['hostname'] = socket.gethostname()
        json_data['capacity'] = self.capacity
                  
        await websocket.send(json.dumps(json_data))

    async def send_image_info(self, websocket):
        ''' 画像情報送信 '''

        while True:
            result, frame = self.capture.read()

            if not result:
                continue

            json_data = {
                'id': self.id,
                'transmissionType': STREAMING,
                'clientType': CAMERA,
                'timestamp': int(time.time()),
                'totalSnedNumber': 0,
                'sendNumber': -1,
                'endPoint': False,
                'data': ''
            }
                        
            frame = cv2.resize(frame, None, fx = 0.5, fy = 0.5)
            frame = cv2.putText(frame, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), (0, 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1, cv2.LINE_AA)
            _, encoded = cv2.imencode('.png', frame)
            base64_data = base64.b64encode(encoded).decode()
                            
            total_sned_number = math.ceil(len(base64_data) / MAX_DIVISION_NUMBER)
            json_data['totalSnedNumber'] = total_sned_number

            for i in range(total_sned_number):
                start_index = i * MAX_DIVISION_NUMBER

                json_data['sendNumber'] = i
                json_data['endPoint'] = total_sned_number - 1 == i
                json_data['data'] = base64_data[start_index : start_index + MAX_DIVISION_NUMBER] if i < total_sned_number else base64_data[start_index : ]

                await websocket.send(json.dumps(json_data))
            
            return

    async def run(self):
        ''' Websocketクライアント実行 '''
        
        self.id = -1

        async with websockets.connect(self.url, ping_timeout=86400) as websocket:
            self.logger.name = __name__

            try:
                while True:
                    msg = await websocket.recv()
                    json_data = json.loads(msg)
                    
                    if json_data['transmissionType'] == CONECT:
                        await self.send_conect_info(websocket, json_data)
                    elif json_data['transmissionType'] == STREAMING:
                        await self.send_image_info(websocket)
                    
            except websockets.ConnectionClosed as err:
                self.logger.error('サーバとの接続が解除されました。')
                self.logger.error(err)
            except Exception as err:
                self.logger.error('エラーが発生しました。')
                self.logger.error(err)