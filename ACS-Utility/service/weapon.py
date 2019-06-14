from typing import List

from model.weapon import Weapon
from service.i_database import DatabaseService
from service.i_dom import DomService


class WeaponService:
    """装備一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService):
        self.dbs = dbs
        self.doms = doms
        self.weapon_list: List[Weapon] = []

    def crawl_for_kammusu(self):
        root_dom = self.doms.create_dom_from_url('http://kancolle.wikia.com/wiki/Equipment')
        print(root_dom)

    def crawl_for_enemy(self):
        root_dom = self.doms.create_dom_from_url('http://kancolle.wikia.com/wiki/List_of_equipment_used_by_the_enemy')
        print(root_dom)

    def dump_to_db(self):
        pass
