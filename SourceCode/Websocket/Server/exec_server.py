#!/usr/bin/python3
# -*- coding: utf-8 -*-

from server import Server
from logging import DEBUG, INFO, ERROR
import asyncio

LOGGER_LEVEL = DEBUG if __debug__ else ERROR

def main():
    ''' メイン関数 '''
    ws_server = Server(LOGGER_LEVEL)
    ws_server.initialize(LOGGER_LEVEL)
    
    try:
        asyncio.run(ws_server.run())
    except Exception as e:
        ws_server.logger.error(e)
        ws_server.logger.info('プログラムを終了しました。')
    
if __name__ == '__main__':
    main()
