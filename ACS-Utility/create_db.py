# -*- coding: utf-8 -*-

import os
import re
import pandas
import sqlite3
import urllib.request
from contextlib import closing
from typing import List
from bs4 import BeautifulSoup
from pprint import pprint

def has_table(cursor, table_name: str) -> bool:
    """{table_name}テーブルの存在を確認する。あればTrueを返す
    """
    command = f"SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND name='{table_name}'"
    cursor.execute(command)
    return cursor.fetchone()[0] != 0

def create_weapon_type_table(cursor) -> None:
    """ 装備種テーブルを作成する
    """
    # 装備種テーブルを作成する
    if has_table(cursor, 'weapon_type'):
        cursor.execute('DROP TABLE weapon_type')
    command = '''CREATE TABLE [weapon_type] (
                 [id] INTEGER NOT NULL UNIQUE,
                 [name] TEXT NOT NULL UNIQUE,
                 [short_name] TEXT NOT NULL UNIQUE,
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 装備種テーブルにデータを追加する
    command = 'INSERT INTO weapon_type (id, name, short_name) VALUES (?,?,?)'
    weapon_type_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'weapon_type.csv'))
    data = list(map(lambda x: (x[0], x[1], x[2]), weapon_type_df.values))
    cursor.executemany(command, data)
    connect.commit()

    # 装備テーブルにインデックスを設定する
    command = 'CREATE INDEX weapon_type_name on weapon_type(name)'
    cursor.execute(command)
    command = 'CREATE INDEX weapon_type_short_name on weapon_type(short_name)'
    cursor.execute(command)

def crawl_friend_weapon_data() -> List[any]:
    """艦娘の装備一覧をクロールして作成する
    """
    # 戦闘行動半径を読み込んでおく
    weapon_radius_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'weapon_radius.csv'))
    weapon_radius_dict: Dict[str, int] = {}
    for pair in weapon_radius_df.values:
        weapon_radius_dict[pair[0]] = pair[1]

    # 装備種一覧を読み込んでおく
    weapon_type_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'weapon_type.csv'))
    weapon_type_dict: Dict[str, int] = {}
    weapon_type_dict2: Dict[str, int] = {}
    weapon_type_dict3: Dict[int, str] = {}
    for pair in weapon_type_df.values:
        if pair[3] not in weapon_type_dict:
            weapon_type_dict[pair[3]] = pair[0]
        weapon_type_dict2[pair[1]] = pair[0]
        weapon_type_dict3[pair[0]] = pair[1]
    #微調整
    weapon_type_dict['Autogyro'] = weapon_type_dict2['対潜哨戒機']
    weapon_type_dict['Extra Armor (Large)'] = weapon_type_dict2['増設バルジ']
    weapon_radius_dict['Midget Submarine'] = weapon_type_dict2['艦載艇']
    weapon_type_dict3[0] = 'なし'

    # Webページを取得してパースする
    weapon_data = [(0,0,'なし',0,0,0,0)]
    with urllib.request.urlopen('http://kancolle.wikia.com/wiki/Equipment') as request:
        # 取得、パース
        soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')
        tr_tag_list = soup.select("table.wikitable tr")

        # 1行づつ読み取っていく
        for trTag in tr_tag_list:
            # 関係ない行は無視する
            td_tag_list = trTag.select("td")
            if len(td_tag_list) < 9:
                continue

            # 装備IDを読み取る
            id = int(td_tag_list[0].text)

            # 装備名を読み取る
            name = td_tag_list[2].text.replace(td_tag_list[2].a.text, '', 1)
            name = re.sub('(^ |\n)', '', name)

            # スペックを読み取る
            raw_stat_icons = list(map(lambda x: re.sub(r".*/([A-Za-z_]+)\.png.*", r"\1", x['href']), td_tag_list[4].select('a')))
            raw_stat_values = re.sub("(<a.*?</a>|<span.*?\">|</span>|\n| )", "", td_tag_list[4].decode_contents(formatter="html"))
            raw_stat_values = re.sub("<br/>", ",", raw_stat_values)
            raw_stat_values = raw_stat_values.split(',')
            status = {}
            for icon, value in zip(raw_stat_icons, raw_stat_values):
                status[icon] = value
            aa = int(status['Icon_AA']) if 'Icon_AA' in status else 0
            accuracy = int(status['Icon_Hit']) if 'Icon_Hit' in status else 0
            interception = int(status['Icon_Interception']) if 'Icon_Interception' in status else 0
            radius = weapon_radius_dict[name] if name in weapon_radius_dict else 0

            # 装備種を読み取る
            weapon_type = re.sub("\n", '', td_tag_list[3].text)
            #辞書による自動判断
            if weapon_type in weapon_type_dict:
                weapon_type = weapon_type_dict[weapon_type]
            else:
                if 'Radar' in weapon_type:
                    if 'Icon_AA' in status:
                        weapon_type = weapon_type_dict2['対空電探']
                    else:
                        weapon_type = weapon_type_dict2['水上電探']
                else:
                    weapon_type = weapon_type_dict2['その他']
            #個別対処
            if weapon_type == weapon_type_dict2['艦上偵察機'] and '彩雲' in name:
                weapon_type = weapon_type_dict2['艦上偵察機(彩雲)']
            if weapon_type == weapon_type_dict2['艦上爆撃機'] and '爆戦' in name:
                weapon_type = weapon_type_dict2['艦上爆撃機(爆戦)']
            if weapon_type == weapon_type_dict2['爆雷投射機'] and '投射機' not in name:
                weapon_type = weapon_type_dict2['爆雷']
            if weapon_type == weapon_type_dict2['局地戦闘機'] and name not in ['雷電', '紫電一一型', '紫電二一型 紫電改', '紫電改(三四三空) 戦闘301']:
                weapon_type = weapon_type_dict2['陸軍戦闘機']

            # データを入力する
            weapon_data.append((id, weapon_type, name, aa, accuracy, interception, radius))
    return weapon_data

def crawl_enemy_weapon_data() -> List[any]:
    """深海棲艦の装備一覧をクロールして作成する
    """
    return []

def crawl_weapon_data() -> List[any]:
    """装備一覧をWebクロールして作成する
    """
    # 艦娘の装備一覧を読み取る
    friend_weapon_data = crawl_friend_weapon_data()

    # 深海棲艦の装備一覧を読み取る
    enemy_weapon_data = crawl_enemy_weapon_data()

    # 合体させたものを戻り値とする
    weapon_data = friend_weapon_data
    weapon_data.extend(enemy_weapon_data)
    return weapon_data

def create_weapon_table(cursor) -> None:
    """ 装備テーブルを作成する
    """
    # 装備テーブルを作成する
    if has_table(cursor, 'weapon'):
        cursor.execute('DROP TABLE weapon')
    command = '''CREATE TABLE [weapon] (
                 [id] INTEGER,
                 [type] INTEGER NOT NULL REFERENCES [weapon_type]([id]),
                 [name] TEXT NOT NULL UNIQUE,
                 [aa] INTEGER NOT NULL,
                 [accuracy] INTEGER NOT NULL,
                 [interception] INTEGER NOT NULL,
                 [radius] INTEGER NOT NULL,
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 装備テーブルにデータを追加する
    command = 'INSERT INTO weapon (id, type, name, aa, accuracy, interception, radius) VALUES (?,?,?,?,?,?,?)'
    data = crawl_weapon_data()
    cursor.executemany(command, data)
    connect.commit()

    # 装備テーブルにインデックスを設定する
    command = 'CREATE INDEX weapon_name on weapon(name)'
    cursor.execute(command)

# 当該Pythonファイルのディレクトリ
ROOT_DIRECTORY = os.path.dirname(__file__)

# データベースファイルの相対ファイルパス
DB_PATH = '../ACS-Server/src/main/webapp/WEB-INF/GameData_.db'
DB_PATH = 'GameData.db'

with closing(sqlite3.connect(os.path.join(ROOT_DIRECTORY, DB_PATH))) as connect:
    cursor = connect.cursor()

    # 装備種テーブルを作成する
    create_weapon_type_table(cursor)

    # 装備テーブルを作成する
    create_weapon_table(cursor)
