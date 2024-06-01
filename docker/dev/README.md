# Docker での環境構築

流れを以下に記載する

## 1. Python 環境の準備

- docker コンテナの build

    ```bash
    $ cd docker/phase2
    $ cp .env.example .env

    $ docker compose build
    ```

## 2. jupyter 起動

    ```bash
    $ docker compose up
    ```

- これで、 `localhost:{JUPYTER_PORT}` に jupyter が立ち上がる
