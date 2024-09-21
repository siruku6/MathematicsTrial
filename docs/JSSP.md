# Job Shop Scheduling (JSSP)

## 1. 環境構築方法

```bash
cd {REPOSITORY_ROOT_DIR}/docker/dev/
cp .env.example .env
docker compose build
docker compose up
```

以上のコマンドを実行すると、WEBブラウザから `localhost:8888` にアクセスすることで Jupyter のトップページを開くことができるようになります。

## 2. 実行方法

### 2-1. データの取得

- [la40 の Taillard specification](http://jobshop.jjvh.nl/instance.php?instance_id=49#:~:text=as%20text%20file.-,Taillard%20specification,-Specification%20according%20to) のデータと、[ta80 の Taillard specification](http://jobshop.jjvh.nl/instance.php?instance_id=163#:~:text=as%20text%20file.-,Taillard%20specification,-Specification%20according%20to) のデータを download。
- `{REPOSITORY_ROOT_DIR}/notebooks/data/jssp/` 以下に `la40.txt` と `ta80.txt` を設置。

### 2-2. directory 構成

以下のようになっていれば大丈夫です。

```
MathematicalTrial/
 ├── docker/         # 環境構築に必要なファイル群
 │    └── dev/
 │         ├── .env
 │         ├── docker-compose.yml
 │         ├── Dockerfile
 │         └── requirements.txt
 │
 ├── docs/           # このファイルがあるディレクトリ
 ├── jssp/           # ソースコード が格納されている
 ├── notebooks/
 │    ├── benchmarks # 最適化処理実行 notebook が格納されている
 │    ├── data       # 各種データを格納
 │    │    └── jssp/ # JSSP 用のデータを格納
 │    │         ├── la40.txt
 │    │         └── ta80.txt
 │    └── ...
 └── README.md
```

※ JSSP に関係のあるディレクトリやファイルのみ記載


### 2-3. notebook の実行

1. 「1. 環境構築方法」を実施
1. WEBブラウザから `localhost:8888` にアクセス
1. パスワード (初期値は `demo`) を入力
1. jupyter `notebooks/benchmarks/` ディレクトリ以下にあるファイルを実行  
※制限時間 (timelimit) などの各種設定は notebook 内で設定可能
    1. 240702_jssp_la40_with_GA.ipynb: GA (二点交叉) で求解
    1. 240830_jssp_la40_simulated_annealing.ipynb: SA で求解
    1. 240908_jssp_la40_ta80_ortools.ipynb: CP-SAT で求解
    1. 240908_jssp_la40_ta80_pulp_youtube.ipynb: CBC で求解
    1. 240702_jssp_la40_with_GA.ipynb: GA (順序に基づく交叉) で求解
