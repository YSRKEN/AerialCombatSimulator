import os

import pandas

from constant import DATA_PATH
from model.kammusu_type import KammusuType
from service.i_database import DatabaseService


class KammusuTypeService:
    """艦種を検索するためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService):
        self.df = pandas.read_csv(os.path.join(DATA_PATH, 'kammusu_type.csv'))
        self.dbs = dbs

    def find_by_name(self, key: str) -> KammusuType:
        """艦種名から艦種情報を検索する
            (ヒットしない場合は「その他」扱いにする)

        Parameters
        ----------
        key
            艦種名

        Returns
        -------
            艦種情報
        """

        # 特殊処理
        if key == '補給艦':
            return self.find_by_name('給油艦')
        result = self.df.query(f"name == '{key}'")
        if len(result) == 0:
            raise Exception(f'不明な艦種名({key})です')
        temp = result.to_dict(orient='records')[0]
        return KammusuType(**temp)

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS kammusu_type')
        command = '''CREATE TABLE kammusu_type (
                 id INTEGER NOT NULL UNIQUE,
                 name TEXT NOT NULL UNIQUE,
                 short_name TEXT NOT NULL UNIQUE,
                 PRIMARY KEY(id))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = 'INSERT INTO kammusu_type (id, name, short_name) VALUES (?,?,?)'
        data = [(x['id'], x['name'], x['short_name']) for x in self.df.to_dict(orient='records')]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        # テーブルにインデックスを設定する
        command = 'CREATE INDEX kammusu_type_name on kammusu_type(name)'
        self.dbs.execute(command)
        command = 'CREATE INDEX kammusu_type_short_name on kammusu_type(short_name)'
        self.dbs.execute(command)
