import re
from pprint import pprint
from typing import List, Tuple

from model.i_dom import Dom
from model.map import Map
from service.i_database import DatabaseService
from service.i_dom import DomService


class MapService:
    """マップ一覧のためのサービスクラス
    """

    def __init__(self, dbs: DatabaseService, doms: DomService):
        self.dbs = dbs
        self.doms = doms
        self.map_list: List[Map] = []

    @staticmethod
    def parse_map_text_link(dom: Dom) -> List[Tuple[str, str]]:
        """DOMをパースして、マップ名とそのURLを取得する

        Parameters
        ----------
        dom
            DOM

        Returns
        -------
            [(マップ名, URL)]
        """
        event_div = dom.select('#EventTemplate')
        li_list = event_div.select_many('ul > li')
        output = []
        for li_tag in li_list:
            a_tag = li_tag.select('a')
            map_link = f'https://kancolle.fandom.com{a_tag.attribute("href", "")}'
            map_text = a_tag.inner_text()
            output.append((map_text, map_link))
        return output

    @staticmethod
    def get_image_url(dom: Dom) -> str:
        """DOMをパースして、マップ画像のURLを取得する

        Parameters
        ----------
        dom
            DOM

        Returns
        -------
            マップ画像のURL
        """
        for img_Tag in dom.select_many('img'):
            width = int(img_Tag.attribute('width', ''))
            height = int(img_Tag.attribute('height', ''))
            alt = img_Tag.attribute('alt', '')
            if width < 0 or height == 0 or ('Map' not in alt):
                continue
            image_url = img_Tag.attribute('data-src', '')
            if image_url == '':
                image_url = img_Tag.attribute('src', '')
            image_url = re.sub('\.png.*', '.png', image_url)
            return image_url

    def crawl(self):
        # 通常海域
        map_index = 1
        while True:
            dom = self.doms.create_dom_from_url(f'https://kancolle.fandom.com/wiki/World_{map_index}')
            if dom is None:
                break

            # マップ名と対応するURLを取得
            text_link_list = self.parse_map_text_link(dom)

            # 対応するURLからマップ画像のURLを抽出
            map_list = [Map(name=x[0], info_url=x[1], image_url=self.get_image_url(self.doms.create_dom_from_url(x[1])))
                        for x in text_link_list]
            self.map_list += map_list
            map_index += 1

    def dump_to_db(self):
        # テーブルを新規作成する
        self.dbs.execute('DROP TABLE IF EXISTS map')
        command = '''CREATE TABLE map (
                name TEXT NOT NULL UNIQUE,
                info_url TEXT NOT NULL UNIQUE,
                image_url TEXT NOT NULL UNIQUE,
                PRIMARY KEY(name))'''
        self.dbs.execute(command)

        # テーブルにデータを追加する
        command = '''INSERT INTO map (name, info_url, image_url) VALUES (?,?,?)'''
        data = [(x.name, x.info_url, x.image_url) for x in self.map_list]
        self.dbs.executemany(command, data)
        self.dbs.commit()
