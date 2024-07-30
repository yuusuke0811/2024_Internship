# -*- coding: utf-8 -*-

from client import Client
from logging import DEBUG, INFO
import asyncio
import time

LOGGER_LEVEL = DEBUG if __debug__ else INFO
RECONECT_SEC = 5

def main():
    ''' メイン関数 '''
    
    # Websocketクライアントクラスをインスタンス化
    ws_client = Client(LOGGER_LEVEL)
    try:
        # 初期化
        ws_client.initialize()        
    except Exception as e:
        ws_client.logger.error(e)
        return
    
    try:
        while True:
            try:
                asyncio.run(ws_client.run())
            except ConnectionRefusedError as e:
                ws_client.logger.error('サーバとの接続に失敗しました。')
            except Exception as e:
                ws_client.logger.error('エラーが発生しました。')
                ws_client.logger.error(e)
                
            ws_client.logger.info(f'{RECONECT_SEC}秒後に再接続を行います。')
            time.sleep(RECONECT_SEC)
    except KeyboardInterrupt:
        ws_client.capture.release()
        ws_client.logger.info('プログラムを終了しました。')

if __name__ == '__main__':   
    main()
    