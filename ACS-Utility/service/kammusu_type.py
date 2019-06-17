import os

import pandas

from constant import DATA_PATH
from service.i_database import DatabaseService


class KammusuTypeService:
    """艦種を検索するためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService):
        self.df = pandas.read_csv(os.path.join(DATA_PATH, 'kammusu_type.csv'))
        self.dbs = dbs

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
