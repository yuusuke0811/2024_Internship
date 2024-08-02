#!/usr/bin/python3
# -*- coding: utf-8 -*-

import asyncio

from websocket_server_transmission_processing import WebsocketServerTransmissionProcessing as Server
from logging import DEBUG, INFO, ERROR

LOGGER_LEVEL = DEBUG if __debug__ else ERROR

def main():
    ''' メイン関数 '''
    ws_server = Server(LOGGER_LEVEL)
    ws_server.initialize()
    
    try:
        asyncio.run(ws_server.run())
    except Exception as e:
        ws_server.logger.error(e)
        ws_server.logger.info('プログラムを終了しました。')
    
if __name__ == '__main__':
    main()
