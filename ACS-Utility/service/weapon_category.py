import os
from typing import List

import pandas

from constant import DATA_PATH
from service.i_database import DatabaseService


class WeaponCategoryService:
    """装備カテゴリを検索するためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService):
        self.df = pandas.read_csv(os.path.join(DATA_PATH, 'weapon_category.csv'))
        self.dbs = dbs

    def find_by_category(self, key: str) -> List[str]:
        """装備カテゴリ名に当てはまる装備種名一覧を返す

        Parameters
        ----------
        key
            装備カテゴリ

        Returns
        -------
            装備種名一覧
        """

        result = self.df.query(f"category == '{key}'")
        return list(result['type'].values)

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS weapon_category')
        command = '''CREATE TABLE weapon_category (
                id INTEGER NOT NULL UNIQUE,
                category TEXT NOT NULL,
                [type] TEXT NOT NULL REFERENCES weapon_type(name),
                PRIMARY KEY(id))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = 'INSERT INTO weapon_category (id, category, type) VALUES (?,?,?)'
        data = [(x['id'], x['category'], x['type']) for x in self.df.to_dict(orient='records')]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        # テーブルにインデックスを設定する
        command = 'CREATE INDEX weapon_category_category on weapon_category(category)'
        self.dbs.execute(command)
