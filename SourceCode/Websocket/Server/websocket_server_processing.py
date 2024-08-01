# -*- coding: utf-8 -*-

from Common.common import delete_directory, read_file
from Common.logger import Logger


from Common.Constant.client_type import CAMERA, VIEWER
from Common.Constant.transmission_type import CONECT

from websocket_server import WebsocketServer

import json
import re
import os
import shutil
import subprocess

class WebsocketServerProcessing(Logger):
    '''Websocketサーバ処理クラス'''

    # コンストラクタ
    def __init__(self, log_level: int):
        ''' コンストラクタ
        
        :param int log_level: ログレベル
        '''

        super().__init__(log_level, 'WebsocketServer.log')

        delete_directory(r'./runs')
        delete_directory(r'./tmp', is_create_dir=True)

        self.receive_data = {}
        self.clients = {
            CAMERA: [ ],
            VIEWER: []
        }

        self.log_level = log_level

    # 初期化処理  
    def initialize(self):
        ''' 初期化処理 '''

        # 設定ファイル読み込み
        self.conf = read_file('serverConfig.json')

        # ネットワーク内に接続している機器の死活チェック
        subprocess.run('./Common/NetworkAliveCheck.sh', stdout=subprocess.DEVNULL)

        # IPアドレスを取得
        sp_ip = subprocess.Popen(['ip', '-4', 'addr', 'show', 'dev', self.conf['websocket']['interface']], encoding='utf-8', stdout=subprocess.PIPE)
        sp_grep = subprocess.Popen(['grep', 'inet'], encoding='utf-8', stdin=sp_ip.stdout, stdout=subprocess.PIPE)
        sp_ip.stdout.close()
        out, err = sp_grep.communicate()
        ip_address = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', out)[0]
        
        self.server = WebsocketServer(host=ip_address, port=self.conf['websocket']['port'], loglevel=self.log_level)
    
    # クライアント接続関数
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

    # クライアント切断関数
    def client_left(self, client, server):
        ''' クライアント切断関数 '''

        self.clients[CAMERA] = [i for i in self.clients[CAMERA] if i['id'] != client['id']]
        self.clients[VIEWER] = [i for i in self.clients[VIEWER] if i['id'] != client['id']]

        # 切断したクライアントの画像格納フォルダを削除
        if os.path.exists(f'./tmp/{client['id']}'):
            shutil.rmtree(f'./tmp/{client['id']}')

        self.logger.info('クライアントとの接続が終了しました。【接続ID： {}】'.format(client['id']))

    # メッセージ送信関数
    def send_data_to_client(self, client, data):
        '''メッセージ送信関数'''
        # メッセージ送信
        self.server.send_message(client, json.dumps(data))
        self.logger.info('クライアントへデータを送信しました。【接続ID： {}】'.format(client['id']))

    # Websocketサーバ起動関数
    def run(self):
        ''' Websocketサーバ起動関数 '''
        
        # クライアント接続時のコールバック関数にself.new_client関数をセット
        self.server.set_fn_new_client(self.new_client)
        # クライアント切断時のコールバック関数にself.client_left関数をセット
        self.server.set_fn_client_left(self.client_left)
