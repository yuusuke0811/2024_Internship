# -*- coding: utf-8 -*-

import pymongo

class DatabaseOperation():
    ''' DB操作クラス '''

    def __init__(self, conf: dict):
        ''' コンストラクタ

        :param dict conf: 接続情報 
        '''

        self.mongo_client = pymongo.MongoClient(conf['host'], conf['port'], username=conf['username'], password=conf['password'])
        self.db = self.mongo_client['websocket_info']
        self.collections = {
            'RegistedClient': self.db['registed_client']
        }
    
    def insert_data(self, target_collection: str, data: dict):
        ''' データ挿入 
        
        :param str target_collection: 対象コレクション
        :param dict data: 挿入データ
        '''
        
        self.collections[target_collection].insert_one(data)
