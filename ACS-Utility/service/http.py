import hashlib
import os

import requests
from dateutil.parser import parse as parse_date

from constant import CACHE_PATH


class HttpService:
    @staticmethod
    def read_text_from_url(url: str, encoding: str) -> str:
        # キャッシュにデータが存在するかを確認する
        response = requests.head(url)
        if response.status_code >= 400:
            return ''
        last_modified = parse_date(response.headers.get('last-modified'))
        timestamp = int(last_modified.timestamp()) * 10 ** 6 + last_modified.microsecond
        cache_path = os.path.join(CACHE_PATH, hashlib.md5((url + f',{timestamp}').encode()).hexdigest())
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding=encoding) as f:
                return f.read()

        # データを読み込む
        print(f'[Add Cache : {url} {last_modified}]')
        response = requests.get(url)
        if not response.ok:
            return ''
        response.encoding = encoding
        output_text = response.text

        # キャッシュに蓄える
        with open(cache_path, 'w', encoding=encoding) as f:
            f.write(output_text)

        return output_text
