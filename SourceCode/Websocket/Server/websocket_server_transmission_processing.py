# -*- coding: utf-8 -*-

import base64
import json
import math
import time
import os
import sys

from threading import Thread

from websocket_server_processing import WebsocketServerProcessing
from image_processing import ImageProcessing
from database_operation import DatabaseOperation

from Constant.models import SEGMENTATION

sys.path.append('../')
from Common.Constant.common import MAX_DIVISION_NUMBER
from Common.Constant.transmission_type import CONECT, STREAMING, CAMERA_CONNECTION_INFO, CAMERA_REGISTRATION_INFO, CAMERA_REGISTERATION, CHANGE_CAMERA_SETTINGS, CAMERA_DELETE 
from Common.Constant.client_type import CAMERA, VIEWER

class WebsocketServerTransmissionProcessing(WebsocketServerProcessing):
    ''' Websocketサーバ伝送処理クラス '''
    
    # コンストラクタ
    def __init__(self, log_level: int):
        ''' コンストラクタ

        :param ing log_level: ログレベル
        '''

        super().__init__(log_level)
    
    # 初期化処理
    def initialize(self):
        ''' 初期化処理  '''

        super().initialize()

        self.straming_thread = Thread(target=self.straming_threading, daemon=True)
        self.analysis_thread = Thread(target=self.analysis_threading, daemon=True)

        self.image_processing = ImageProcessing()
        self.database_operation = DatabaseOperation(self.conf['database'])

    # Websocketサーバ起動関数
    def run(self):
        ''' Websocketサーバ起動関数 '''

        # ストリーミングスレッド開始
        self.straming_thread.start()
        # 解析スレット開始
        self.analysis_thread.start()

        super().run()
        # メッセージ受信時のコールバック関数にself.message_received関数をセット
        self.server.set_fn_message_received(self.message_received)
        # サーバ起動
        self.server.run_forever()

    # ストリーミングスレッド関数
    def straming_threading(self):
        ''' ストリーミングスレッド関数 '''

        while True:
            for cameraClient in self.clients[CAMERA]:

                # Websocketサーバ情報からクライアントの接続情報を取得
                client = next((x for x in self.server.clients if x['id'] == cameraClient['id']), None)
                
                # 該当しない場合はスキップ
                if client == None:
                    # 未接続のクライアント情報を削除
                    self.clients[CAMERA] = [i for i in self.clients[CAMERA] if i['id'] != client['id']]
                    continue

                # カメラ登録済み 
                if cameraClient['isRegisted']:
                    # ストリーミングOFF or 処理中の場合はスキップ
                    if (not cameraClient['isStreaming']) or cameraClient['isProcess']:
                        continue
                # カメラ未登録の場合はスキップ
                else:
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

    # 解析スレッド関数
    def analysis_threading(self):
        ''' 解析スレッド関数 '''

        while True:
            for cameraClient in self.clients[CAMERA]:
                # 画像ファイルが0枚の場合はスキップ
                if len(cameraClient['image_path']) == 0:
                    continue

                # 最新の画像パスの要素番号を取得
                index = len(cameraClient['image_path']) - 1
                
                try:
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
                except:
                    continue
            
            time.sleep(1)

    # メッセージ受信関数
    def message_received(self, client, server, message):
        '''  メッセージ受信関数 '''
        self.logger.info('クライアントからメッセージを受信しました。【接続ID： {}】'.format(client['id']))

        # JSONに変換
        json_data = json.loads(message)
        if type(json_data) is str:
            json_data = (json.loads(json_data))

        transmission_type = json_data['transmissionType']

        # 伝送種別が「0x00：接続」の場合
        if transmission_type == CONECT:
            self.connection_process(client, json_data)

        # 伝送種別が「0x01：ストリーミング」の場合
        elif transmission_type == STREAMING:
            self.streaming_process(client, json_data)
        
        # 伝送種別が「0x10：カメラ接続情報要求」の場合
        elif transmission_type == CAMERA_CONNECTION_INFO:
            self.get_camera_connection_info(client, json_data)
        
        # 伝送種別が「0x11：カメラ登録情報要求」の場合 
        elif transmission_type == CAMERA_REGISTRATION_INFO:
            self.get_camera_registration_info(client, json_data)
        
        # 伝送種別が「0x20：カメラ登録要求」の場合
        elif transmission_type == CAMERA_REGISTERATION:
            self.regist_camera(client, json_data)
        
        # 伝送種別が「0x21：カメラ設定変更要求」の場合
        elif transmission_type == CHANGE_CAMERA_SETTINGS:
            self.change_setting_camera(client, json_data)
        
        # 伝送種別が「0x25：カメラ削除要求」の場合
        elif transmission_type == CAMERA_DELETE:
            self.delete_camera(client, json_data)
        
        # 不明な伝送種別の場合
        else:
            print(json_data['transmissionType'])

    # 接続処理関数
    def connection_process(self, client, json_data):
        ''' 接続処理関数 '''

        clientType = json_data['clientType']
        
        # クライアントが「カメラ」の場合
        if clientType == CAMERA:
            clientInfo = {
                'id': client['id'],
                'objectId': None,
                'address': client['address'][0],
                'hostname': json_data['hostname'],
                'name': '', 
                'count':0,
                'capacity': json_data['capacity'],
                'isRegisted': True,
                'isProcess': False,
                'isStreaming': True,
                'image_path': [],
            }

            # カメラ登録情報を取得
            registedCameraInfo = self.database_operation.find_one_data('registedCameraInfo', { 'hostname': json_data['hostname'] })
            if registedCameraInfo is not None:
                clientInfo['isRegisted'] = True

                clientInfo['objectId'] = registedCameraInfo['objectId']
                clientInfo['name'] = registedCameraInfo['name']
                clientInfo['isStreaming'] = registedCameraInfo['isStreaming']

            self.clients[clientType].append(clientInfo)
        # クライアントが「ビューアー」の場合
        elif clientType == VIEWER:
            self.clients[clientType].append({
                'id': client['id'],
                'selectCameraId': -1,
                'modelType': SEGMENTATION
            })

    # ストリーミング処理関数
    def streaming_process(self, client, json_data):
        ''' ストリーミング処理関数 '''          
                    
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

    # カメラ接続情報関数
    def get_camera_connection_info(self, client, json_data):
        ''' カメラ接続情報関数 '''

        json_data['data'] = self.clients[CAMERA]
        self.send_data_to_client(client, json_data)

    # カメラ登録情報関数
    def get_camera_registration_info(self, client, json_data):
        ''' カメラ登録情報関数 '''

        json_data['data'] = self.clients[CAMERA]
        self.send_data_to_client(client, json_data)

    # カメラ登録関数
    def regist_camera(self, client, json_data):
        ''' カメラ登録関数 '''
        self.send_data_to_client(client, json_data)

    # カメラ設定変更関数
    def change_setting_camera(self, client, json_data):
        ''' カメラ設定変更関数 '''

        self.send_data_to_client(client, json_data)

    # カメラ削除関数
    def delete_camera(self, client, json_data):
        ''' カメラ削除関数 '''

        self.send_data_to_client(client, json_data)
