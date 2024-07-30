# -*- coding: utf-8 -*-

import os
import shutil
import json

def delete_directory(target_dir: str, is_create_dir: bool = False):
    ''' ディレクトリ削除

    :param str target_dir: 対象ディレクトリ
    :param bool is_create_dir: ディレクトリ作成フラグ（デフォルト： False）
    '''

    # 対象のディレクトリが存在するかチェック
    if os.path.exists(target_dir):  
        # 存在する場合は削除
        shutil.rmtree(target_dir)

    # 作成フラグがTrueの場合
    if is_create_dir:
        os.mkdir(target_dir)

def read_file(target_file: str):
    ''' ファイル読み込み
    
    :param str target_file: 対象ファイル

    :return: ファイルデータ
    :rtype: Any | bytes
    '''

    data = None

    with open(target_file, 'rb') as f:
        # JSONファイルの場合
        if 'json' in target_file:
            data = json.load(f)
        else:
            data = f.read()

    return data