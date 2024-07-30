# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os

class Logger:
    ''' ロガークラス
    '''
    def __init__(self, log_level: int, log_file: str, max_bytes: int = 100000000, backup_count = 10):
        ''' コンストラクタ

        :param int log_level: ログレベル
        :param str log_file: ログファイル名
        :param int max_bytes: ログ最大保存容量（デフォルト：100MB）
        :param int backup_count: ログファイルバックアップ世代数（デフォルト：10）
        '''

        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)

        save_dir = r'./log'
        # ログ出力ディレクトリがあるかチェック
        if not os.path.exists(save_dir):
            # 無ければ作成
            os.mkdir(save_dir)

        # 出力フォーマット
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s %(message)s')

        # ログファイル出力設定
        file_handler = logging.handlers.RotatingFileHandler(os.path.join(save_dir, log_file), maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
    
        # ストリーミング出力設定
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)

        # ログハンドラ設定
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        