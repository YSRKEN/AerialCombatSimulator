from typing import List

from model.position import Position
from model.position_fleet import PositionFleet
from service.formation_category import FormationCategoryService
from service.i_database import DatabaseService
from service.i_dom import DomService
from service.map import MapService


class PositionService:
    """座標一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService, ms: MapService, fcs: FormationCategoryService):
        self.dbs = dbs
        self.doms = doms
        self.ms = ms
        self.fcs = fcs
        self.position_list: List[Position] = []
        self.position_fleet_list: List[PositionFleet] = []

    def crawl(self):
        pass

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS position')
        command = '''CREATE TABLE position (
                id INTEGER,
                map TEXT REFERENCES [map]([name]),
                name TEXT,
                final_flg INTEGER NOT NULL,
                formation INTEGER REFERENCES formation_category(id),
                PRIMARY KEY(id))'''
        self.dbs.execute(command)
        self.dbs.execute('DROP TABLE IF EXISTS position_fleet')
        command = '''CREATE TABLE position_fleet (
                position INTEGER REFERENCES position(id),
                fleet_index INTEGER NOT NULL,
                unit_index INTEGER NOT NULL,
                enemy INTEGER REFERENCES kammusu(id),
                PRIMARY KEY(position, fleet_index, unit_index))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = '''INSERT INTO position (id,map,name,final_flg,formation) VALUES (?,?,?,?,?)'''
        data = [(x.id, x.map, x.name, x.final_flg, x.formation) for x in self.position_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        command = '''INSERT INTO position_fleet (position,fleet_index,unit_index,enemy) VALUES (?,?,?,?)'''
        data = [(x.position, x.fleet_index, x.unit_index, x.enemy) for x in self.position_fleet_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()
