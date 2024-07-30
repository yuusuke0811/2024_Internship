# Docker環境構築  

* ca-certificatesおよびcurlインストール

    ``` bash
    > sudo apt -y install ca-certificates curl
    ```  

* 公式のGPGキーを取得

    ``` bash
    > sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    ```

* 公式のDockerリポジトリを追加

    ``` bash
    > echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

* パッケージリスト更新

    ``` bash
    > sudo apt update
    ```

* Dockerのインストール

    ``` bash
    > sudo apt -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

* ユーザをdockerグループ

    ``` bash
    > sudo usermod -aG docker $USER
    ```

* 変更を反映

    ``` bash
    > newgrp docker
    ```
