import os

import pandas

from constant import DATA_PATH
from service.i_database import DatabaseService


class FormationCategoryService:
    """陣形カテゴリを検索するためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService):
        self.df = pandas.read_csv(os.path.join(DATA_PATH, 'formation_category.csv'))
        self.dbs = dbs

    def find_by_wikia_alt_name(self, key: str) -> int:
        """陣形カテゴリ名に当てはまる陣形カテゴリIDを返す

        Parameters
        ----------
        key
            陣形カテゴリ名

        Returns
        -------
            陣形カテゴリID
        """

        result = self.df.query(f"wikia_alt_name == '{key}'")
        return int(result['id'].values[0])

    def find_by_wikia_span_name(self, key: str) -> int:
        """陣形カテゴリ名に当てはまる陣形カテゴリIDを返す

        Parameters
        ----------
        key
            陣形カテゴリ名

        Returns
        -------
            陣形カテゴリID
        """

        result = self.df.query(f"wikia_span_name == '{key}'")
        return int(result['id'].values[0])

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS formation_category')
        command = '''CREATE TABLE formation_category (
                id INTEGER NOT NULL UNIQUE,
                category TEXT NOT NULL,
                PRIMARY KEY(id))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = 'INSERT INTO formation_category (id, category) VALUES (?,?)'
        data = [(x['id'], x['name']) for x in self.df.to_dict(orient='records')]
        self.dbs.executemany(command, data)
        self.dbs.commit()
