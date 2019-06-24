import json
from pprint import pprint
from typing import List

from model.kammusu import Kammusu
from service.http import HttpService
from service.i_database import DatabaseService
from service.i_dom import DomService
from service.kammusu_type import KammusuTypeService
from service.weapon import WeaponService


class KammusuService:
    """艦娘一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService, https: HttpService, ws: WeaponService, kts: KammusuTypeService):
        self.dbs = dbs
        self.doms = doms
        self.https = https
        self.ws = ws
        self.kts = kts
        self.kammusu_list: List[Kammusu] = [Kammusu(0, 0, '', 0, 0, [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], True, 0, 0, 0)]

    def crawl_kammusu(self):
        # デッキビルダーから艦娘データを読み込む
        raw_text = self.https.read_text_from_url('http://kancolle-calc.net/data/shipdata.js', 'UTF-8')
        raw_data = json.loads(raw_text.replace('var gShips = ', ''))

        # 各種データを読み込む
        for record in raw_data:
            # 艦船ID
            kammusu_id = int(record['id'])
            if kammusu_id >= 1501:
                continue

            # 艦種
            kammusu_type = self.kts.find_by_name(record['type'])

            # 艦名
            kammusu_name = record['name']
            if 'なし' in kammusu_name:
                continue

            # 対空
            kammusu_aa = record['max_aac']

            # スロットサイズ
            kammusu_slot_size = record['slot']

            # 搭載数
            kammusu_slot = record['carry']
            slot_len = len(kammusu_slot)
            for _ in range(slot_len, 5):
                kammusu_slot.append(0)

            # 初期装備
            kammusu_weapon = record['equip']
            slot_len = len(kammusu_weapon)
            for _ in range(slot_len, 5):
                kammusu_weapon.append(0)

            # 火力
            kammusu_attack = record['max_fire']

            # 雷装
            kammusu_torpedo = record['max_torpedo']

            # 対潜
            kammusu_anti_sub = record['max_ass']

            self.kammusu_list.append(Kammusu(kammusu_id, kammusu_type.id, kammusu_name, kammusu_aa, kammusu_slot_size,
                                             kammusu_slot, kammusu_weapon, True, kammusu_attack, kammusu_torpedo,
                                             kammusu_anti_sub))

    def crawl_enemy(self):
        # DOMを読み込む
        root_dom = self.doms.create_dom_from_url('https://kancolle.fandom.com/wiki/Enemy_Vessels/Full')

        # テーブルを1行づつ読み込む
        for tr_tag in root_dom.select_many('table.wikitable tr'):
            # 不要な行を飛ばす
            td_tag_list = tr_tag.select_many('td')
            if len(td_tag_list) < 20:
                continue

            # 艦船ID
            enemy_id = int(td_tag_list[1].inner_text())

            # 艦種
            enemy_type = self.kts.find_by_wikia_name(td_tag_list[0].inner_text().replace(' ', '').replace('\n', ''))

            # 艦名
            enemy_name = td_tag_list[4].inner_text().replace('\n', '')

            # 対空
            enemy_aa_str = td_tag_list[9].inner_text()
            if 'nil' in enemy_aa_str:
                continue
            enemy_aa = int(enemy_aa_str)

            # スロット
            if td_tag_list[18].inner_text() == '\n':
                enemy_slot = []
            else:
                enemy_slot = [int(x.replace('\n', '')) for x in td_tag_list[18].inner_text().split(',')]
            enemy_slot_size = len(enemy_slot)
            for _ in range(enemy_slot_size, 5):
                enemy_slot.append(0)

            # 初期装備
            enemy_weapon = [self.ws.find_by_url(x.attribute('href', '').replace('/wiki/', '')).id for x in td_tag_list[19].select_many('a')]
            for _ in range(enemy_slot_size, 5):
                enemy_weapon.append(0)

            # 火力
            enemy_attack_str = td_tag_list[7].inner_text()
            if 'nil' in enemy_attack_str:
                continue
            enemy_attack = int(enemy_attack_str)

            # 雷装
            enemy_torpedo_str = td_tag_list[8].inner_text()
            if 'nil' in enemy_torpedo_str:
                continue
            enemy_torpedo = int(enemy_torpedo_str)

            # 対潜
            enemy_anti_sub_str = td_tag_list[11].inner_text()
            if 'nil' in enemy_anti_sub_str:
                continue
            enemy_anti_sub = int(enemy_anti_sub_str)

            self.kammusu_list.append(Kammusu(enemy_id, enemy_type.id, enemy_name, enemy_aa, enemy_slot_size,
                                             enemy_slot, enemy_weapon, False, enemy_attack, enemy_torpedo,
                                             enemy_anti_sub))

    def dump_to_db(self):
        pprint(self.kammusu_list)

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
