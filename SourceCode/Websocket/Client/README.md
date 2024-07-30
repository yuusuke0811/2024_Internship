# Websocketクライアント環境構築

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

* openCV関連ライブラリのインストール

    ``` bash
    > sudo apt -y install libopencv-dev
    ```

* Websocketインストール  

    ``` pip
    > pip install websocket
    ```
