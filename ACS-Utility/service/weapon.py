import re
from pprint import pprint
from typing import List, Dict
import urllib.parse

from model.i_dom import Dom
from model.weapon import Weapon
from service.i_database import DatabaseService
from service.i_dom import DomService
from service.weapon_category import WeaponCategoryService
from service.weapon_type import WeaponTypeService


class WeaponService:
    """装備一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService, wts: WeaponTypeService, wcs: WeaponCategoryService):
        self.dbs = dbs
        self.doms = doms
        self.wts = wts
        self.wcs = wcs
        self.weapon_list: List[Weapon] = [Weapon(0, 0, '', 0, 0, 0, 0, False, 0, 0, 0, 0)]

    @staticmethod
    def convert_name(dom: Dom) -> str:
        """装備名のDOMから装備名を抽出する

        Parameters
        ----------
        dom
            装備名のDOM

        Returns
        -------
            装備名
        """

        all_inner_text = dom.inner_text()
        a_inner_text = dom.select('a').inner_text()
        return re.sub('(^ |\n)', '', all_inner_text.replace(a_inner_text, '', 1))

    def read_radius(self, url: str) -> int:
        """装備のURLから戦闘行動半径を抽出する

        Parameters
        ----------
        url
            装備のURL

        Returns
        -------
            戦闘行動半径
        """

        print(f'    read_radius({urllib.parse.quote(url, safe=":/")})')
        page_dom = self.doms.create_dom_from_url(url)
        data_dom = page_dom.select('div#kc-eq-flights')
        if data_dom is None:
            return 0
        return int(data_dom.select('b').inner_text().replace('Combat Radius: ', ''))

    @staticmethod
    def convert_spec(dom: Dom) -> Dict[str, str]:
        """装備性能のDOMから装備性能を抽出する

        Parameters
        ----------
        dom
            装備性能のDOM

        Returns
        -------
            {カテゴリ: 性能値}

        """
        raw_icons = [re.sub(r".*/Icon_([A-Za-z_]+)\.png.*", r"\1", x.attribute('href', '')) for x in dom.select_many('a')]
        raw_values = re.sub("(<a.*?</a>|<span.*?\">|</span>|\n| )", "", dom.inner_html())
        raw_values = raw_values.split('<br>')
        spec_dict = dict(zip(raw_icons, raw_values))
        return spec_dict

    def crawl_for_kammusu(self):
        # DOMを読み込む
        root_dom = self.doms.create_dom_from_url('https://kancolle.fandom.com/wiki/Equipment')

        # テーブルを1行づつ読み込む
        lbas_set = set(self.wcs.find_by_category('LBAS'))
        for tr_tag in root_dom.select_many('tr'):
            # 不要な行を飛ばす
            td_tag_list = tr_tag.select_many('td')
            if len(td_tag_list) < 9:
                continue

            # 各種情報を読み取る
            # IDと名前はそのまま読み取れる
            weapon_id = int(td_tag_list[0].inner_text())
            weapon_name = self.convert_name(td_tag_list[2])

            # スペック情報は「Stats」列から読み取れる
            weapon_spec = self.convert_spec(td_tag_list[4])
            weapon_aa = int(weapon_spec['AA']) if 'AA' in weapon_spec else 0
            weapon_accuracy = int(weapon_spec['Hit']) if 'Hit' in weapon_spec else 0
            weapon_interception = int(weapon_spec['Interception']) if 'Interception' in weapon_spec else 0
            weapon_attack = int(weapon_spec['Gun']) if 'Gun' in weapon_spec else 0
            weapon_torpedo = int(weapon_spec['Torpedo']) if 'Torpedo' in weapon_spec else 0
            weapon_antisub = int(weapon_spec['ASW']) if 'ASW' in weapon_spec else 0
            weapon_bomber = int(weapon_spec['Dive']) if 'Dive' in weapon_spec else 0

            # 装備種情報はWikia名から変換する
            weapon_type_text = td_tag_list[3].inner_text().replace('\n', '')
            weapon_type = self.wts.find_by_wikia_name(weapon_type_text, weapon_name, weapon_aa)

            # 戦闘行動半径は再度HTTPリクエストを叩く必要があるので注意
            weapon_radius = 0
            if weapon_type.name in lbas_set:
                url = 'https://kancolle.fandom.com' + td_tag_list[2].select('a').attribute('href', '')
                weapon_radius = self.read_radius(url)

            self.weapon_list.append(Weapon(weapon_id, weapon_type.id, weapon_name, weapon_aa, weapon_accuracy,
                                           weapon_interception, weapon_radius, True, weapon_attack, weapon_torpedo,
                                           weapon_antisub, weapon_bomber))

    def crawl_for_enemy(self):
        # DOMを読み込む
        root_dom = self.doms.create_dom_from_url('https://kancolle.fandom.com/wiki/List_of_equipment_used_by_the_enemy')

        # テーブルを1行づつ読み込む
        for tr_tag in root_dom.select_many('table.wikitable tr'):
            # 不要な行を飛ばす
            td_tag_list = tr_tag.select_many('td')
            if len(td_tag_list) < 6:
                continue

            # 装備IDを読み取る
            weapon_id = int(td_tag_list[0].inner_text())

            # 装備名を読み取る
            weapon_name = self.convert_name(td_tag_list[2])

            # スペック情報は「Stats」列から読み取れる
            weapon_spec = self.convert_spec(td_tag_list[4])
            weapon_aa = int(weapon_spec['AA']) if 'AA' in weapon_spec else 0
            weapon_accuracy = int(weapon_spec['Hit']) if 'Hit' in weapon_spec else 0
            weapon_interception = int(weapon_spec['Interception']) if 'Interception' in weapon_spec else 0
            weapon_attack = int(weapon_spec['Gun']) if 'Gun' in weapon_spec else 0
            weapon_torpedo = int(weapon_spec['Torpedo']) if 'Torpedo' in weapon_spec else 0
            weapon_antisub = int(weapon_spec['ASW']) if 'ASW' in weapon_spec else 0
            weapon_bomber = int(weapon_spec['Dive']) if 'Dive' in weapon_spec else 0

            # 装備種情報はWikia名から変換する
            weapon_type_text = td_tag_list[3].inner_text().replace('\n', '')
            weapon_type = self.wts.find_by_wikia_name(weapon_type_text, weapon_name, weapon_aa)

            # 敵装備の戦闘行動半径は考えなくていい
            weapon_radius = 0

            self.weapon_list.append(Weapon(weapon_id, weapon_type.id, weapon_name, weapon_aa, weapon_accuracy,
                                           weapon_interception, weapon_radius, False, weapon_attack, weapon_torpedo,
                                           weapon_antisub, weapon_bomber))

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS weapon')
        command = '''CREATE TABLE weapon (
                     id INTEGER,
                     type INTEGER NOT NULL REFERENCES weapon_type(id),
                     name TEXT NOT NULL,
                     aa INTEGER NOT NULL,
                     accuracy INTEGER NOT NULL,
                     interception INTEGER NOT NULL,
                     radius INTEGER NOT NULL,
                     for_kammusu_flg INTEGER NOT NULL,
                     attack INTEGER NOT NULL,
                     torpedo INTEGER NOT NULL,
                     anti_sub INTEGER NOT NULL,
                     bomber INTEGER NOT NULL,
                     PRIMARY KEY(id))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = 'INSERT INTO weapon (id, type, name, aa, accuracy, interception, radius, for_kammusu_flg, attack,' \
                  'torpedo, anti_sub, bomber) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'
        data = [(x.id, x.type, x.name, x.aa, x.accuracy, x.interception, x.radius, x.for_kammusu_flg, x.attack,
                 x.torpedo, x.anti_sub, x.bomber) for x in self.weapon_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        # テーブルにインデックスを設定する
        command = 'CREATE INDEX weapon_name on weapon(name)'
        self.dbs.execute(command)
        command = 'CREATE INDEX weapon_for_kammusu_flg on weapon(for_kammusu_flg)'
        self.dbs.execute(command)
