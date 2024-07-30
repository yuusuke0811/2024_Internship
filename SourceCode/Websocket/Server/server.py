# -*- coding: utf-8 -*-

from Common.common import delete_directory, read_file
from Common.logger import Logger
from image_processing import ImageProcessing
from database_operation import DatabaseOperation

from Common.Constant.common import MAX_DIVISION_NUMBER
from Common.Constant.transmission_type import CONECT, STREAMING, CAMERA_INFO, VERIFICATION, CHANGE_MODEL, CHANGE_CAMERA
from Common.Constant.client_type import CAMERA, VIEWER
from Constant.models import SEGMENTATION

from websocket_server import WebsocketServer
from threading import Thread

import base64
import shutil
import json
import math
import time
import os
import subprocess
import re

class Server(Logger):
    ''' Websocketサーバクラス '''

    def __init__(self, log_level: int):
        ''' コンストラクタ 
        
        :param int log_level: ログレベル
        '''
        
        super().__init__(log_level, 'WebsocketServer.log')

        delete_directory(r'./runs')
        delete_directory(r'./tmp', True)

        self.receive_data = {}
        self.clients = {
            CAMERA: [ ],
            VIEWER: [ ]
        }

    def initialize(self, log_level: int):
        ''' 初期化処理
        
        :param int log_level: ログレベル
        '''
        
        # 設定ファイル読み込み
        conf = read_file('serverConfig.json')
            
        # ネットワーク内に接続している機器の死活チェック
        subprocess.run('./Common/NetworkAliveCheck.sh', stdout=subprocess.DEVNULL)

        # IPアドレスを取得
        sp_ip = subprocess.Popen(['ip', '-4', 'addr', 'show', 'dev', conf['websocket']['interface']], encoding='utf-8', stdout=subprocess.PIPE)
        sp_grep = subprocess.Popen(['grep', 'inet'], encoding='utf-8', stdin=sp_ip.stdout, stdout=subprocess.PIPE)
        sp_ip.stdout.close()
        out, err = sp_grep.communicate()
        ip_address = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', out)[0]
        
        # 各種、インスタンス化
        self.image_processing = ImageProcessing()
        self.database_operation = DatabaseOperation(conf['database'])
        self.server = WebsocketServer(host=ip_address, port=conf['websocket']['port'], loglevel=log_level)
        self.straming_thread = Thread(target=self.straming_threading, daemon=True)
        self.analysis_thread = Thread(target=self.analysis_threading, daemon=True)

    def straming_threading(self):
        ''' ストリーミングスレッド '''

        while True:
            for cameraClient in self.clients[CAMERA]:
                # Websocketサーバ情報からクライアントの接続情報を取得
                client = next((x for x in self.server.clients if x['id'] == cameraClient['id']), None)

                # 処理中の場合はスキップ
                if cameraClient['isProcess']:
                    continue
                # 該当しない場合はスキップ
                elif client == None:
                    # 未接続のクライアント情報を削除
                    self.clients[CAMERA] = [i for i in self.clients[CAMERA] if i['id'] != client['id']]
                    continue

                # 伝送データを作成
                json_data = {
                    'id': client['id'],
                    'transmissionType': STREAMING
                }

                # クライアントへメッセージ送信
                self.send_data_to_client(client, json_data)
                # 処理中フラグを「処理中」に変更
                cameraClient['isProcess'] = True

                # 次のクライアントへの送信処理まで500msスリープ
                time.sleep(0.75)

            # 1sスリープ
            time.sleep(1)

    def analysis_threading(self):
        ''' 解析スレッド '''

        while True:
            for cameraClient in self.clients[CAMERA]:
                if len(cameraClient['image_path']) > 0:
                    # 最新の画像パスの要素番号を取得
                    index = len(cameraClient['image_path']) - 1
                    file_path, count = self.image_processing.exec_image_process(cameraClient['image_path'][index], SEGMENTATION)
            
                    # キャパシティを格納
                    cameraClient['count'] = count

                    with open(file_path, 'rb') as f:
                        base64_data = base64.b64encode(f.read()).decode()

                    json_data = {
                        'id': cameraClient['id'],
                        'capacity': cameraClient['capacity'],
                        'transmissionType': STREAMING
                    }

                    totalSnedNumber = math.ceil(len(base64_data) / MAX_DIVISION_NUMBER)
                    json_data['totalSnedNumber'] = totalSnedNumber

                    for i in range(totalSnedNumber):
                        startIndex = i * MAX_DIVISION_NUMBER

                        json_data['sendNumber'] = i
                        json_data['endPoint'] = totalSnedNumber - 1 == i
                        json_data['data'] = base64_data[startIndex : startIndex + MAX_DIVISION_NUMBER] if i < totalSnedNumber else base64_data[startIndex : ]

                        for viewerClient in self.clients[VIEWER]:
                            client = next((x for x in self.server.clients if x['id'] == viewerClient['id']), None)
                        
                            if client == None:
                                self.clients[VIEWER] = [i for i in self.clients[VIEWER] if i['id'] != client['id']]
                                continue

                            self.send_data_to_client(client, json_data)
            
            time.sleep(1)

    def send_data_to_client(self, client, data):
        '''メッセージ送信関数'''
        # メッセージ送信
        self.server.send_message(client, json.dumps(data))
        self.logger.info('クライアントへデータを送信しました。【接続ID： {}】'.format(client['id']))

    def new_client(self, client, server):
        ''' クライアント接続関数 '''
        self.logger.info('クライアントの接続が開始されました。【接続ID： {}】'.format(client['id']))

        json_data = {
            'id': client['id'],
            'transmissionType': CONECT,
            'message': '接続が開始されました。',
        }

        # クライアントへメッセージ送信
        self.send_data_to_client(client, json_data)

    def client_left(self, client, server):
        ''' クライアント切断関数 '''

        self.clients[CAMERA] = [i for i in self.clients[CAMERA] if i['id'] != client['id']]
        self.clients[VIEWER] = [i for i in self.clients[VIEWER] if i['id'] != client['id']]

        # 切断したクライアントの画像格納フォルダを削除
        if os.path.exists(f'./tmp/{client['id']}'):
            shutil.rmtree(f'./tmp/{client['id']}')

        self.logger.info('クライアントとの接続が終了しました。【接続ID： {}】'.format(client['id']))

    def message_received(self, client, server, message):
        '''  クライアントからのメッセージ受信関数 '''
        self.logger.info('クライアントからメッセージを受信しました。【接続ID： {}】'.format(client['id']))

        # JSONに変換
        json_data = json.loads(message)
        if type(json_data) is str:
            json_data = (json.loads(json_data))

        # 伝送種別が「接続」の場合
        if json_data['transmissionType'] == CONECT:
            clientType = json_data['clientType']

            # クライアントが「カメラ」の場合
            if clientType == CAMERA:
                self.clients[clientType].append({
                    'id': client['id'],
                    'address': client['address'][0],
                    'hostname': json_data['hostname'],
                    'count':0,
                    'capacity': json_data['capacity'],
                    'isProcess': False,
                    'image_path': [],
                })
            # クライアントが「ビューアー」の場合
            elif clientType == VIEWER:
                self.clients[clientType].append({
                    'id': client['id'],
                    'selectCameraId': -1,
                    'modelType': SEGMENTATION
                })

        # 伝送種別が「ストリーミング」の場合
        elif json_data['transmissionType'] == STREAMING:
            # 画像情報格納
            self.image_processing.image_data_store(json_data)

            # データ終点
            if (json_data['endPoint']):
                # カメラのクライアント情報を取得
                cameraClient = next((x for x in self.clients[CAMERA] if x['id'] == client['id']), None)
                
                file_path = self.image_processing.image_save(json_data)
                cameraClient['image_path'].append(file_path)
                # 保存数が3件の場合
                if len(cameraClient['image_path']) > 3:
                    delete_file_path = cameraClient['image_path'].pop(0)
                    os.remove(delete_file_path)

                cameraClient['isProcess'] = False

        # 伝送種別が「検証」の場合
        elif json_data['transmissionType'] == VERIFICATION:
            # 画像情報格納
            self.image_processing.image_data_store(json_data)

            # データ終点
            if (self.json_data['endPoint']):
                file_path = self.image_processing.exec_image_process(json_data, json_data['modelType'])

                if file_path == '':
                    return

                with open(file_path, 'rb') as f:
                    base64_data = base64.b64encode(f.read).decode()

                    totalSnedNumber = math.ceil(len(base64_data) / MAX_DIVISION_NUMBER)
                    json_data['totalSnedNumber'] = totalSnedNumber

                    for i in range(totalSnedNumber):
                        json_data['sendNumber'] = i
                        json_data['endPoint'] = totalSnedNumber - 1 == i
                        json_data['data'] = base64_data[startIndex : startIndex + MAX_DIVISION_NUMBER] if i < totalSnedNumber else base64_data[startIndex : ]

                        self.send_data_to_client(client, json_data)

        # 伝送種別が「カメラ情報」の場合
        elif json_data['transmissionType'] == CAMERA_INFO:
            json_data['data'] = self.clients[CAMERA]

            self.send_data_to_client(client, json_data)

        # 伝送種別が「モデル変更」の場合
        elif json_data['transmissionType'] == CHANGE_MODEL:
            viewerClient = next((x for x in self.clients[VIEWER] if x['id'] == client['id']), None)
            viewerClient['modelType'] = json_data['modelType']

        # 伝送種別が「カメラ変更」の場合
        elif json_data['transmissionType'] == CHANGE_CAMERA:
            viewerClient = next((x for x in self.clients[VIEWER] if x['id'] == client['id']), None)
            if (viewerClient != None):
                viewerClient['selectCameraId'] = json_data['selectCameraId']

        else:
            print(json_data['transmissionType'])

    def run(self):
        ''' Websocketサーバ起動 '''

        # ストリーミングスレッド開始
        self.straming_thread.start()
        # 解析スレット開始
        self.analysis_thread.start()

        # クライアント接続時のコールバック関数にself.new_client関数をセット
        self.server.set_fn_new_client(self.new_client)
        # クライアント切断時のコールバック関数にself.client_left関数をセット
        self.server.set_fn_client_left(self.client_left)
        # メッセージ受信時のコールバック関数にself.message_received関数をセット
        self.server.set_fn_message_received(self.message_received)
        # サーバ起動
        self.server.run_forever()
