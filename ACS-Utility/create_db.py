# -*- coding: utf-8 -*-

import os
import re
import pandas
import sqlite3
import urllib.request
from contextlib import closing
from typing import List, Dict
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

def create_weapon_category_table(cursor) -> None:
    """ 装備カテゴリテーブルを作成する
    """
    # 装備カテゴリテーブルを作成する
    if has_table(cursor, 'weapon_category'):
        cursor.execute('DROP TABLE weapon_category')
    command = '''CREATE TABLE [weapon_category] (
                 [id] INTEGER NOT NULL UNIQUE,
                 [name] TEXT NOT NULL UNIQUE,
                 [short_name] TEXT NOT NULL UNIQUE,
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

def get_weapon_type_dict():
    """装備種と装備種IDとの対応表を作成する
    """
    # 装備種一覧を読み込んでおく
    weapon_type_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'weapon_type.csv'))
    weapon_type_default_dict: Dict[str, int] = {}
    weapon_type_wikia_dict: Dict[str, int] = {}
    for pair in weapon_type_df.values:
        if pair[3] not in weapon_type_wikia_dict:
            weapon_type_wikia_dict[pair[3]] = pair[0]
        weapon_type_default_dict[pair[1]] = pair[0]

    # 微調整
    weapon_type_wikia_dict['Autogyro'] = weapon_type_default_dict['対潜哨戒機']
    weapon_type_wikia_dict['Extra Armor (Large)'] = weapon_type_default_dict['増設バルジ']
    weapon_type_wikia_dict['Midget Submarine'] = weapon_type_default_dict['艦載艇']
    weapon_type_wikia_dict['Special Amphibious Tank'] = weapon_type_default_dict['艦載艇']
    weapon_type_wikia_dict['Carrier-based Reconnaissance Aircraft (II)'] = weapon_type_default_dict['艦上偵察機']
    weapon_type_wikia_dict['Submarine Torpedo'] = weapon_type_default_dict['魚雷']
    weapon_type_wikia_dict['Large Caliber Main Gun (II)'] = weapon_type_default_dict['大口径主砲']
    weapon_type_wikia_dict['Large Sonar'] = weapon_type_default_dict['ソナー']

    return weapon_type_default_dict, weapon_type_wikia_dict

def calc_weapon_name(td_tag) -> str:
    """装備名を算出する
    """
    name = td_tag.text.replace(td_tag.a.text, '', 1)
    return re.sub('(^ |\n)', '', name)

def calc_weapon_status(td_tag):
    """装備ステータスを算出する
    """
    # アイコンのファイル名を取り出す
    raw_stat_icons = list(map(lambda x: re.sub(r".*/([A-Za-z_]+)\.png.*", r"\1", x['href']), td_tag.select('a')))

    # 各数値を取り出す
    raw_stat_values = re.sub("(<a.*?</a>|<span.*?\">|</span>|\n| )", "", td_tag.decode_contents(formatter="html"))
    raw_stat_values = re.sub("<br/>", ",", raw_stat_values)
    raw_stat_values = raw_stat_values.split(',')

    # アイコン名と数値とをzipする
    status = {}
    for icon, value in zip(raw_stat_icons, raw_stat_values):
        status[icon] = value

    # 各数値を読み取る
    aa = int(status['Icon_AA']) if 'Icon_AA' in status else -1
    accuracy = int(status['Icon_Hit']) if 'Icon_Hit' in status else 0
    interception = int(status['Icon_Interception']) if 'Icon_Interception' in status else 0

    return aa, accuracy, interception

def calc_weapon_type(td_tag, name, aa, weapon_type_default_dict, weapon_type_wikia_dict) -> int:
    """装備種を算出する
    """
    # 当該文字列を取得する
    weapon_type = re.sub("\n", '', td_tag.text)

    #辞書による自動判断
    if weapon_type in weapon_type_wikia_dict:
        weapon_type = weapon_type_wikia_dict[weapon_type]
    else:
        if 'Radar' in weapon_type:
            # レーダー系の中で対空値が付いている場合は対空電探とする
            if aa >= 0:
                weapon_type = weapon_type_default_dict['対空電探']
            else:
                weapon_type = weapon_type_default_dict['水上電探']
        else:
            weapon_type = weapon_type_default_dict['その他']

    # 個別ケースに対処
    if weapon_type == weapon_type_default_dict['艦上偵察機'] and '彩雲' in name:
        weapon_type = weapon_type_default_dict['艦上偵察機(彩雲)']
    if weapon_type == weapon_type_default_dict['艦上爆撃機'] and '爆戦' in name:
        weapon_type = weapon_type_default_dict['艦上爆撃機(爆戦)']
    if weapon_type == weapon_type_default_dict['爆雷投射機'] and '投射機' not in name:
        weapon_type = weapon_type_default_dict['爆雷']
    if weapon_type == weapon_type_default_dict['局地戦闘機'] and name not in ['雷電', '紫電一一型', '紫電二一型 紫電改', '紫電改(三四三空) 戦闘301']:
        weapon_type = weapon_type_default_dict['陸軍戦闘機']

    return weapon_type

def crawl_friend_weapon_data() -> List[any]:
    """艦娘の装備一覧をクロールして作成する
    """
    # 戦闘行動半径を読み込んでおく
    weapon_radius_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'weapon_radius.csv'))
    weapon_radius_dict: Dict[str, int] = {}
    for pair in weapon_radius_df.values:
        weapon_radius_dict[pair[0]] = pair[1]

    # 装備種一覧を読み込んでおく
    weapon_type_default_dict, weapon_type_wikia_dict = get_weapon_type_dict()

    # Webページを取得してパースする
    weapon_data = [(0,0,'なし',0,0,0,0,1)]
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
            name = calc_weapon_name(td_tag_list[2])

            # スペックを読み取る
            aa, accuracy, interception = calc_weapon_status(td_tag_list[4])
            radius = weapon_radius_dict[name] if name in weapon_radius_dict else 0

            # 装備種を読み取る
            weapon_type = calc_weapon_type(td_tag_list[3], name, aa, weapon_type_default_dict, weapon_type_wikia_dict)

            # データを入力する
            aa = aa if aa >= 0 else 0
            weapon_data.append((id, weapon_type, name, aa, accuracy, interception, radius, 1))
    return weapon_data

def crawl_enemy_weapon_data() -> List[any]:
    """深海棲艦の装備一覧をクロールして作成する
    """

    # 装備種一覧を読み込んでおく
    weapon_type_default_dict, weapon_type_wikia_dict = get_weapon_type_dict()

    # Webページを取得してパースする
    weapon_data = []
    with urllib.request.urlopen('http://kancolle.wikia.com/wiki/List_of_equipment_used_by_the_enemy') as request:
        # 取得、パース
        soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')
        tr_tag_list = soup.select("table.wikitable tr")

        # 1行づつ読み取っていく
        for trTag in tr_tag_list:
            # 関係ない行は無視する
            td_tag_list = trTag.select("td")
            if len(td_tag_list) < 6:
                continue
            
            # 装備IDを読み取る
            id = int(td_tag_list[0].text)

            # 装備名を読み取る
            name = calc_weapon_name(td_tag_list[2])

            # スペックを読み取る
            aa, accuracy, interception = calc_weapon_status(td_tag_list[4])

            # 装備種を読み取る
            weapon_type = calc_weapon_type(td_tag_list[3], name, aa, weapon_type_default_dict, weapon_type_wikia_dict)

            # データを入力する
            aa = aa if aa >= 0 else 0
            weapon_data.append((id, weapon_type, name, aa, accuracy, 0, 0, 0))
    return weapon_data

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
                 [name] TEXT NOT NULL,
                 [aa] INTEGER NOT NULL,
                 [accuracy] INTEGER NOT NULL,
                 [interception] INTEGER NOT NULL,
                 [radius] INTEGER NOT NULL,
                 [for_kammusu_flg] INTEGER NOT NULL,
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 装備テーブルにデータを追加する
    command = 'INSERT INTO weapon (id, type, name, aa, accuracy, interception, radius, for_kammusu_flg) VALUES (?,?,?,?,?,?,?,?)'
    data = crawl_weapon_data()
    cursor.executemany(command, data)
    connect.commit()

    # 装備テーブルにインデックスを設定する
    command = 'CREATE INDEX weapon_name on weapon(name)'
    cursor.execute(command)
    command = 'CREATE INDEX weapon_for_kammusu_flg on weapon(for_kammusu_flg)'
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

    # 装備カテゴリテーブルを作成する
    create_weapon_category_table(cursor)

    # 装備テーブルを作成する
    create_weapon_table(cursor)
