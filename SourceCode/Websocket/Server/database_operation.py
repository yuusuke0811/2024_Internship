# -*- coding: utf-8 -*-

import pymongo

class DatabaseOperation():
    ''' DB操作クラス '''

    # コンストラクタ
    def __init__(self, conf: dict):
        ''' コンストラクタ

        :param dict conf: 接続情報 
        '''

        self.mongo_client = pymongo.MongoClient(conf['host'], conf['port'], username=conf['username'], password=conf['password'])
        self.db = self.mongo_client['websocketClientDB']
        self.collections = {
            'registedCameraInfo': self.db['registedCameraInfo']
        }

    # データ全件検索
    def find_data(self, target_collection: str):
        ''' データ検索
        
        :param str target_collection: 対象コレクション
        '''
        return self.collections[target_collection].find()
    
    # データ一件検索（条件）
    def find_one_data(self, target_collection, conditions: dict):
        ''' データ検索（条件）
        
        :param str target_collection: 対象コレクション
        :param dir target_collection: 検索条件
        '''

        return self.collections[target_collection].find_one(conditions)
    
    # データ挿入
    def insert_data(self, target_collection: str, data: dict):
        ''' データ挿入 
        
        :param str target_collection: 対象コレクション
        :param dict data: 挿入データ
        :return: 挿入件数
        :rtype: int
        '''
        
        return self.collections[target_collection].insert_one(data)

    # データ更新
    def update_data(self, target_collection: str, conditions: dict, data: dict):
        ''' データ更新 
        
        :param str target_collection: 対象コレクション
        :param dict conditons: 条件
        :param dict data: 更新データ
        :return: 更新件数
        :rtype: int
        '''

        return self.collections[target_collection].update_one(conditions,  {'$set': data} )

    # データ削除
    def delete_data(self, target_collection: str, conditions: dict):
        ''' データ削除

        :param str target_collection: 対象コレクション
        :param dict conditions: 条件
        :return: 削除件数
        :rtype: int
        '''

        return self.collections[target_collection].delete_one(conditions)
    