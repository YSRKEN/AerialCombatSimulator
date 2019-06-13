import os

# 基準となるディレクトリ
BASE_PATH = os.path.dirname(__file__)

# キャッシュデータを入れるためのディレクトリ
CACHE_PATH = os.path.join(BASE_PATH, 'cache')

# データファイルが置かれているディレクトリ
DATA_PATH = os.path.join(BASE_PATH, 'data')
