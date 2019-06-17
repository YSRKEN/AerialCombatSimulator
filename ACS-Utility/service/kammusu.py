from typing import List

import requests

from model.kammusu import Kammusu
from service.i_database import DatabaseService
from service.i_dom import DomService


class KammusuService:
    """艦娘一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService):
        self.dbs = dbs
        self.doms = doms
        self.kammusu_list: List[Kammusu] = [Kammusu(0, 0, '', 0, 0, [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], True, 0, 0, 0)]

    def crawl_kammusu(self):
        # デッキビルダーから艦娘データを読み込む
        raw_data = requests.get('http://kancolle-calc.net/data/shipdata.js').json()
        print(raw_data)
        pass

    def crawl_enemy(self):
        pass

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS kammusu')
        command = '''CREATE TABLE kammusu (
                id INTEGER NOT NULL UNIQUE,
                type INTEGER NOT NULL REFERENCES kammusu_type(id),
                name TEXT NOT NULL,
                aa INTEGER NOT NULL,
                slot_size INTEGER NOT NULL,
                slot1 INTEGER NOT NULL,
                slot2 INTEGER NOT NULL,
                slot3 INTEGER NOT NULL,
                slot4 INTEGER NOT NULL,
                slot5 INTEGER NOT NULL,
                weapon1 INTEGER NOT NULL REFERENCES weapon(id),
                weapon2 INTEGER NOT NULL REFERENCES weapon(id),
                weapon3 INTEGER NOT NULL REFERENCES weapon(id),
                weapon4 INTEGER NOT NULL REFERENCES weapon(id),
                weapon5 INTEGER NOT NULL REFERENCES weapon(id),
                kammusu_flg INTEGER NOT NULL,
                attack INTEGER NOT NULL,
                torpedo INTEGER NOT NULL,
                anti_sub INTEGER NOT NULL,
                PRIMARY KEY(id))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = '''INSERT INTO kammusu (id, type, name, aa, slot_size, slot1, slot2, slot3, slot4, slot5,
                    weapon1, weapon2, weapon3, weapon4, weapon5, kammusu_flg, attack, torpedo, anti_sub)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        data = [(x.id, x.type, x.name, x.aa, x.slot_size, x.slot[0], x.slot[1], x.slot[2], x.slot[3], x.slot[4],
                 x.weapon[0], x.weapon[1], x.weapon[2], x.weapon[3], x.weapon[4], x.kammusu_flg, x.attack,
                 x.torpedo, x.anti_sub) for x in self.kammusu_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        # テーブルにインデックスを設定する
        command = 'CREATE INDEX kammusu_name on kammusu(name)'
        self.dbs.execute(command)
