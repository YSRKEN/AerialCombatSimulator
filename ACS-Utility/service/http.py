import os
import hashlib

import requests

from constant import CACHE_PATH


class HttpService:
    @staticmethod
    def read_text_from_url(url: str, encoding: str) -> str:
        # キャッシュにデータが存在するかを確認する
        cache_path = os.path.join(CACHE_PATH, hashlib.md5(url.encode()).hexdigest())
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding=encoding) as f:
                return f.read()

        # データを読み込む
        response = requests.get(url)
        if not response.ok:
            return ''
        response.encoding = encoding
        output_text = response.text

        # キャッシュに蓄える
        with open(cache_path, 'w', encoding=encoding) as f:
            f.write(output_text)

        return output_text
