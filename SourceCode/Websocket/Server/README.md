# Websocketサーバ環境構築

* pipインストール  

    ``` bash
    > sudo apt -y install python3-pip
    ```  

* pip設定(PEP 686対策)  

    ``` bash
    > mkdir ~/.pip  
    > vi ~/.pip/pip.conf
    ```

    * 設定内容（pip.conf）  
  
          > [global]  
          > break-system-packages = true

* openCVインストール  

      ``` pip
      > pip install opencv-python
      ```

* Websocket Serverインストール  

    ``` pip
    > pip install websocket-server
    ```

* pytorchインストール  
    * CPU  
        
        ``` pip  
        > pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu  
        ```

     * GPU  

        ``` pip  
        > pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        ```

* YOLOインストール  

    ``` pip
    > pip install ultralytics
    ```

* pymongoインストール  

    ``` pip
    > pip install pymongo
    ```
