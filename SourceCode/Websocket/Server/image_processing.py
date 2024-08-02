# -*- coding: utf-8 -*-

from Constant.models import DETECTION, SEGMENTATION, POSE, OBB, CLASS, MOTION

from ultralytics import YOLO

import numpy as np
import os
import base64
import cv2

class ImageProcessing():
    ''' 画像処理クラス '''
    
    def __init__(self):
        ''' コンストラクタ '''
        
        # モデル読み込み
        self.models = {
           # DETECTION: YOLO('yolov8n.pt'),
            SEGMENTATION: YOLO('yolov8n-seg.pt'),
            # POSE: YOLO('yolov8n-pose.pt'),
            # OBB: YOLO('yolov8n-obb.pt'),
            # CLASS: YOLO('yolov8n-cls.pt'),
            # MOTION: ''
        }

        self.receive_data = {}
        self.before_frame = None

    def image_data_store(self, json_data):
        ''' 画像データ格納 '''
        timestamp = json_data['timestamp']
        
        if (timestamp not in self.receive_data):
            self.receive_data[timestamp] = []

        self.receive_data[timestamp].append(json_data['data'])
    
    def image_save(self, json_data):
        '''画像保存'''
        timestamp = json_data['timestamp']
        file_path = None

        # 受信した画像データを取得
        base64_datas = list(filter(lambda x : x != '', self.receive_data[timestamp]))
        # データ容量が等しい場合
        if (len(base64_datas) == json_data['totalSnedNumber']):
            dir_path = f'./tmp/{json_data["id"]}'

            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            file_path = os.path.join(dir_path, f'{timestamp}.png') 

            base64_data = base64.b64decode(''.join(base64_datas).encode())

            # Base64からopenCV形式に変換
            img_raw = np.frombuffer(base64_data, np.uint8)       
            img = cv2.imdecode(img_raw, cv2.IMREAD_COLOR)

            # 画像を保存 
            cv2.imwrite(file_path, img)

            del self.receive_data[timestamp]

        return file_path 

    def exec_image_process(self, file_path, model):
        ''' 画像処理実行 '''
        img = cv2.imread(file_path)

        # 検出処理（YOLO）
        if model != MOTION:
            self.before_frame = None

            model = self.models[model]
            results = model.predict(img, save=True, conf=0.5, show_conf=False, show_boxes=False, classes=[0])
            
            file_path = os.path.join(results[0].save_dir, results[0].path)
        
            names = results[0].boxes.cls
            boxes = results[0].boxes.xyxy
            
            if results[0].masks is not None:
                masks = results[0].masks.xy
                
                for name, mask in zip(names, masks):
                    xys = np.empty((0, 2), int)

                    for xy in mask:
                        cv2.circle(img, ([int(xy[0]), int(xy[1])]), 1, (255,255,255), thickness=1, lineType=cv2.LINE_8, shift=0)
                        xys = np.append(xys, np.array([[int(xy[0]), int(xy[1])]]), axis=0)
                    
                    cv2.fillConvexPoly(img, xys, (255, 0, 0))
            
            cv2.imwrite(file_path,img)

        return file_path, len(names)