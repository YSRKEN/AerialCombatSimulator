import os

import pandas

from constant import DATA_PATH
from model.weapon_type import WeaponType
from service.i_database import DatabaseService


class WeaponTypeService:
    """装備種を検索するためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService):
        self.df = pandas.read_csv(os.path.join(DATA_PATH, 'weapon_type.csv'))
        self.dbs = dbs

    def find_by_wikia_name(self, key: str) -> WeaponType:
        """Wikiaにおける登録名から装備種情報を検索する
            (ヒットしない場合は「その他」扱いにする)

        Parameters
        ----------
        key
            Wikiaにおける登録名

        Returns
        -------
            装備種情報
        """
        result = self.df.query(f"wikia_name == '{key}'")
        if len(result) == 0:
            return self.find_by_wikia_name('Other')
        temp = result.to_dict(orient='records')[0]
        return WeaponType(**temp)

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS weapon_type')
        command = '''CREATE TABLE weapon_type (
                     id INTEGER NOT NULL UNIQUE,
                     name TEXT NOT NULL UNIQUE,
                     short_name TEXT NOT NULL UNIQUE,
                     PRIMARY KEY(id))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = 'INSERT INTO weapon_type (id, name, short_name) VALUES (?,?,?)'
        data = [(x['id'], x['name'], x['short_name']) for x in self.df.to_dict(orient='records')]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        # テーブルにインデックスを設定する
        command = 'CREATE INDEX weapon_type_name on weapon_type(name)'
        self.dbs.execute(command)
        command = 'CREATE INDEX weapon_type_short_name on weapon_type(short_name)'
        self.dbs.execute(command)
