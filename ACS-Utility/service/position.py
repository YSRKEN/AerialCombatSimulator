import re
from pprint import pprint
from typing import List, Tuple

from model.i_dom import Dom
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

    @staticmethod
    def get_scrollable_div_list(dom: Dom) -> List[Dom]:
        """「マップのマスと敵編成一覧」情報を取り出す

        Parameters
        ----------
        dom
            DOM

        Returns
        -------
            (通常マップは1マップにつき1つ、イベント時は難易度の数だけ取得)
        """

        # 普通にCSSセレクトしてヒットすればそこで終了
        output = dom.select_many('div.scrollable')
        if len(output) != 0:
            return output

        # 少し特殊な判定をして、該当するDOMを見つけ出す
        output = []
        for div_tag in dom.select_many('div'):
            style_text = div_tag.attribute('style', '')
            if 'max-height:' not in style_text:
                continue
            if 'overflow-y:auto:' not in style_text:
                continue
            if 'overflow-x:hidden:' not in style_text:
                continue
            output.append(div_tag)
        return output

    def read_position_data(self, dom: Dom) -> List[Tuple[Position, List[List[int]]]]:
        """「マップのマスと敵編成一覧」をパースする

        Parameters
        ----------
        dom
            DOM

        Returns
        -------
            List[Tuple(マス情報・敵編成情報)}
        """
        output: List[Tuple[Position, List[List[int]]]] = []
        for table_tag in dom.select_many('table'):
            # 戦闘しないテーブルは無視する
            th_text = ','.join([x.inner_text() for x in table_tag.select_many('th')])
            if 'Empty Node' in th_text:
                continue
            if 'Resource Node' in th_text:
                continue
            if 'Air Raids' in th_text:
                continue

            # テーブルの中でtdを持つtr一覧を取得する
            tr_tag_list = [x for x in table_tag.select_many('tr') if len(x.select_many('td')) != 0]

            # マス名と敵編成を読み取る
            point_name = ''
            pattern_index = 1
            first_flg = True
            for tr_tag in tr_tag_list:
                td_tag_list = tr_tag.select_many('td')

                # 最初のtrは、tdとしてマス名を含むので取得する
                if first_flg:
                    point_name = td_tag_list[0].inner_text().replace("\n", '')

                # 敵編成が記録されているtdの位置を判断する
                enemy_data_index = -1
                for index, td_tag in enumerate(td_tag_list):
                    if len(td_tag.select_many('a.link-internal')) > 0:
                        enemy_data_index = index
                        break
                if enemy_data_index == -1:
                    continue

                # 敵編成を読み取る
                a_list = td_tag_list[enemy_data_index].select_many('a.link-internal')
                enemy_list = []
                for a_tag in a_list:
                    # 旗艦の位置だけspanタグと併用してaタグを2段重ねにしているので、
                    # 余計なタグを無視するようにする
                    img_tag = a_tag.select('img')
                    if int(img_tag.attribute('width', '0')) < 100:
                        continue

                    # 敵IDを読み取る
                    enemy_id = int(re.sub(r'.*\((\d+)\):.*', r'\1', a_tag.attribute('title', '')))
                    enemy_list.append(enemy_id)

                # ラスダン編成かどうかを判断する
                final_flg = '(Final)' in ','.join([x.inner_text() for x in td_tag_list])

                # 敵の陣形を読み取る
                img_tag_list = td_tag_list[1 if first_flg else 0].select_many('img')
                if len(img_tag_list) > 0:
                    formation_image_tag = img_tag_list[0]
                    formation_image_alt = formation_image_tag.attribute('alt', '')
                    formation_id = self.fcs.find_by_wikia_alt_name(formation_image_alt)
                else:
                    formation_span_tag = td_tag_list[1 if first_flg else 0].select('span')
                    formation_span_text = formation_span_tag.inner_text()
                    formation_id = self.fcs.find_by_wikia_span_name(formation_span_text)

                # 書き込み用に出力
                position = Position(id=0, map=0, name=f'{point_name}-{pattern_index}', final_flg=final_flg,
                                    map_level=0, formation=formation_id)
                if len(enemy_list) <= 6:
                    enemy_data = [enemy_list, []]
                else:
                    enemy_data = [enemy_list[0:6], enemy_list[6:]]
                    if len(enemy_list[6:]) != 6:
                        print(f'{point_name}-{pattern_index}')
                        print(enemy_data)
                        exit()
                output.append((position, enemy_data))

                # 次のループに向けた処理
                if first_flg:
                    first_flg = False
                pattern_index += 1
        return output

    def crawl(self):
        for map_data in self.ms.map_list:
            print(f'　{map_data.name}')
            dom = self.doms.create_dom_from_url(map_data.info_url)

            # 「マップのマスと敵編成一覧」情報を取り出す
            scrollable_div_list = self.get_scrollable_div_list(dom)

            # 「マップのマスと敵編成一覧」をパースして順次代入する
            for map_level_index, scrollable_div_tag in enumerate(scrollable_div_list):
                raw_position_list = self.read_position_data(scrollable_div_tag)
                pprint(raw_position_list)

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS position')
        command = '''CREATE TABLE position (
                id INTEGER,
                map TEXT REFERENCES [map]([name]),
                name TEXT,
                final_flg INTEGER NOT NULL,
                map_level INTEGER NOT NULL,
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
        command = '''INSERT INTO position (id,map,name,final_flg,map_level,formation) VALUES (?,?,?,?,?,?)'''
        data = [(x.id, x.map, x.name, x.final_flg, x.map_level, x.formation) for x in self.position_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()

        command = '''INSERT INTO position_fleet (position,fleet_index,unit_index,enemy) VALUES (?,?,?,?)'''
        data = [(x.position, x.fleet_index, x.unit_index, x.enemy) for x in self.position_fleet_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()
