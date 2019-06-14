import re
from pprint import pprint
from typing import List

from model.i_dom import Dom
from model.weapon import Weapon
from service.i_database import DatabaseService
from service.i_dom import DomService
from service.weapon_type import WeaponTypeService


class WeaponService:
    """装備一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService, wts: WeaponTypeService):
        self.dbs = dbs
        self.doms = doms
        self.wts = wts
        self.weapon_list: List[Weapon] = []

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

    def crawl_for_kammusu(self):
        # DOMを読み込む
        root_dom = self.doms.create_dom_from_url('https://kancolle.fandom.com/wiki/Equipment')

        # テーブルを1行づつ読み込む
        for tr_tag in root_dom.select_many('tr'):
            # 不要な行を飛ばす
            td_tag_list = tr_tag.select_many('td')
            if len(td_tag_list) < 9:
                continue

            # 各種情報を読み取る
            weapon_id = int(td_tag_list[0].inner_text())
            weapon_name = self.convert_name(td_tag_list[2])
            weapon_aa = 0

            weapon_type_text = td_tag_list[3].inner_text().replace('\n', '')
            weapon_type = self.wts.find_by_wikia_name(weapon_type_text, weapon_name, weapon_aa)
            print(f'{weapon_id}\t{weapon_name}\t\t{weapon_type.short_name}')

    def crawl_for_enemy(self):
        root_dom = self.doms.create_dom_from_url('https://kancolle.fandom.com/wiki/List_of_equipment_used_by_the_enemy')
        print(root_dom)

    def dump_to_db(self):
        pprint(self.weapon_list)
