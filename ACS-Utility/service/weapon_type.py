import os
from typing import Dict

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

        self.wikia_to_type_id: Dict[str, int] = {}
        for record in self.df.to_dict(orient='records'):
            self.wikia_to_type_id[record['wikia_name']] = record['id']
        extra_df = pandas.read_csv(os.path.join(DATA_PATH, 'weapon_type_wikia.csv'))
        for record in extra_df.to_dict(orient='records'):
            self.wikia_to_type_id[record['wikia_name']] = record['id']

    def find_by_name(self, key: str) -> WeaponType:
        """装備種名から装備種情報を検索する
            (ヒットしない場合は「その他」扱いにする)

        Parameters
        ----------
        key
            装備種名

        Returns
        -------
            装備種情報
        """

        result = self.df.query(f"name == '{key}'")
        if len(result) == 0:
            return self.find_by_name('その他')
        temp = result.to_dict(orient='records')[0]
        return WeaponType(**temp)

    def find_by_id(self, key: int) -> WeaponType:
        """IDから装備種情報を検索する
            (ヒットしない場合は「その他」扱いにする)

        Parameters
        ----------
        key
            ID

        Returns
        -------
            装備種情報
        """

        result = self.df.query(f"id == '{key}'")
        if len(result) == 0:
            return self.find_by_name('その他')
        temp = result.to_dict(orient='records')[0]
        return WeaponType(**temp)

    def find_by_wikia_name(self, key: str, name: str = '', aa: int = 0) -> WeaponType:
        """Wikiaにおける登録名から装備種情報を検索する
            (ヒットしない場合は「その他」扱いにする)

        Parameters
        ----------
        key
            Wikiaにおける登録名
        name
            装備名
        aa
            装備の対空値

        Returns
        -------
            装備種情報
        """

        # 辞書にヒットする場合
        if key in self.wikia_to_type_id:
            weapon_type_id = self.wikia_to_type_id[key]
            # 特殊処理：一部の装備種における特別裁定
            if weapon_type_id == self.wikia_to_type_id['Carrier-based Reconnaissance Aircraft'] and '彩雲' in name:
                weapon_type_id = self.wikia_to_type_id['Carrier-based Reconnaissance Aircraft(Saiun)']
            if weapon_type_id == self.wikia_to_type_id['Carrier-based Dive Bomber'] and '爆戦' in name:
                weapon_type_id = self.wikia_to_type_id['Carrier-based Dive Bomber(Bakusen)']
            if weapon_type_id == self.wikia_to_type_id['Depth Charge'] and '投射機' not in name:
                weapon_type_id = self.wikia_to_type_id['Depth Charge(Body)']
            if weapon_type_id == self.wikia_to_type_id['Land-based Fighter']:
                if '雷電' not in name and '紫電' not in name and '烈風' not in name:
                    weapon_type_id = self.wikia_to_type_id['Land-based Fighter(II)']
            return self.find_by_id(weapon_type_id)

        # 特殊処理：電探に関する処理
        if 'Radar' in key:
            # レーダー系の中で対空値が付いている場合は対空電探とする
            if aa >= 0:
                return self.find_by_name('水上電探')
            else:
                return self.find_by_name('対空電探')

        return self.find_by_name('その他')

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
