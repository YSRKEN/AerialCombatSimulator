# -*- coding: utf-8 -*-

import os
import re
import pandas
import json
import sqlite3
import urllib.request
from contextlib import closing
from typing import List, Dict
from bs4 import BeautifulSoup
from pprint import pprint
import lxml.html
import lxml.cssselect


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
                [category] TEXT NOT NULL,
                [type] TEXT NOT NULL,
                PRIMARY KEY([id]));'''
    cursor.execute(command)

    # 装備カテゴリテーブルにデータを追加する
    command = 'INSERT INTO weapon_category (id, category, type) VALUES (?,?,?)'
    weapon_category_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'weapon_category.csv'))
    data = list(map(lambda x: (x[0], x[1], x[2]), weapon_category_df.values))
    cursor.executemany(command, data)
    connect.commit()

    # 装備カテゴリテーブルにインデックスを設定する
    command = 'CREATE INDEX weapon_category_category on weapon_category(category)'
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

    # 辞書による自動判断
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


def get_kammusu_type_dict():
    """艦種と艦種IDとの対応表を作成する
    """
    # 装備種一覧を読み込んでおく
    kammusu_type_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'kammusu_type.csv'))
    kammusu_type_dict: Dict[str, int] = {}
    kammusu_type_wikia_dict: Dict[str, int] = {}
    for pair in kammusu_type_df.values:
        kammusu_type_dict[pair[1]] = pair[0]
        kammusu_type_wikia_dict[pair[3]] = pair[0]

    # 微調整
    kammusu_type_dict['補給艦'] = kammusu_type_dict['給油艦']

    return kammusu_type_dict, kammusu_type_wikia_dict


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
    weapon_data = []
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
    weapon_data = [(0, 0, 'なし', 0, 0, 0, 0, 1)]
    weapon_data.extend(friend_weapon_data)
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


def create_kammusu_type_table(cursor) -> None:
    """ 艦種テーブルを作成する
    """
    # 艦種テーブルを作成する
    if has_table(cursor, 'kammusu_type'):
        cursor.execute('DROP TABLE kammusu_type')
    command = '''CREATE TABLE [kammusu_type] (
                 [id] INTEGER NOT NULL UNIQUE,
                 [name] TEXT NOT NULL UNIQUE,
                 [short_name] TEXT NOT NULL UNIQUE,
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 艦種テーブルにデータを追加する
    command = 'INSERT INTO kammusu_type (id, name, short_name) VALUES (?,?,?)'
    kammusu_type_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'kammusu_type.csv'))
    data = list(map(lambda x: (x[0], x[1], x[2]), kammusu_type_df.values))
    cursor.executemany(command, data)

    # 艦種テーブルにインデックスを設定する
    command = 'CREATE INDEX kammusu_type_name on kammusu_type(name)'
    cursor.execute(command)
    command = 'CREATE INDEX kammusu_type_short_name on kammusu_type(short_name)'
    cursor.execute(command)


def crawl_friend_kammusu_data_deckbuilder() -> List[any]:
    """艦娘一覧をクロールして作成する(デッキビルダーから)
    """

    # 艦種一覧を読み込んでおく
    kammusu_type_dict, kammusu_type_wikia_dict = get_kammusu_type_dict()

    # JavaScriptを読み込み、そこからデータを取り出す
    kammusu_data = []
    with urllib.request.urlopen('http://kancolle-calc.net/data/shipdata.js') as request:
        # JSONを読み込む
        json_data_list = json.loads(request.read().decode('utf-8').replace('var gShips = ', ''))

        # 各種データを読み込む
        for json_data in json_data_list:
            # 艦船ID
            id = int(json_data['id'])
            if id >= 1501:
                continue

            # 艦種
            kammusu_type = kammusu_type_dict[json_data['type']]

            # 艦名
            name = json_data['name']
            if 'なし' in name:
                continue

            # 対空
            aa = json_data['aac']

            # スロットサイズ
            slot_size = json_data['slot']

            # 搭載数
            slot = json_data['carry']
            slot_size_2 = len(slot)
            for _ in range(slot_size_2, 5):
                slot.append(0)

            # 初期装備
            weapon = json_data['equip']
            slot_size_2 = len(weapon)
            for _ in range(slot_size_2, 5):
                weapon.append(0)

            # 配列に追加する
            data = (id, kammusu_type, name, aa, slot_size,
                    slot[0], slot[1], slot[2], slot[3], slot[4],
                    weapon[0], weapon[1], weapon[2], weapon[3], weapon[4],
                    1)
            kammusu_data.append(data)
    return kammusu_data


def crawl_friend_kammusu_data_wikia() -> List[any]:
    """艦娘一覧をクロールして作成する(英Wikiから、書きかけ)
    """

    # 艦種一覧を読み込んでおく
    kammusu_type_dict, kammusu_type_wikia_dict = get_kammusu_type_dict()

    # まず、艦娘装備のURLとIDとの対応表を入手する
    weapon_url_id_dict = {}
    with urllib.request.urlopen('http://kancolle.wikia.com/wiki/Equipment') as request:
        # 取得、パース
        soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')
        tr_tag_list = soup.select("div tr")

        # 1行づつ読み取っていく
        for trTag in tr_tag_list:
            # 関係ない行は無視する
            td_tag_list = trTag.select("td")
            if len(td_tag_list) < 9:
                continue

            # 装備IDを読み取る
            id = int(td_tag_list[0].text)

            # URLを読み取る
            url = td_tag_list[2].select('a')[0]['href']

            weapon_url_id_dict[url] = id

    print(weapon_url_id_dict)

    # 次に、艦名の一覧を読み取っておく
    kammusu_dict = {}
    with urllib.request.urlopen('http://kancolle.wikia.com/wiki/Ship') as request:
        # 取得、パース
        soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')
        tr_tag_list = soup.select("div tr")

        # 1行づつ読み取っていく
        for trTag in tr_tag_list:
            # 関係ない行は無視する
            td_tag_list = trTag.select("td")
            if len(td_tag_list) != 2:
                continue

            # 2列めにある対象のaタグを取り込む
            a_tag_list = td_tag_list[1].select('a')
            for a_tag in a_tag_list:
                name = a_tag.text
                href = a_tag['href']
                kammusu_dict[href] = name

    print(kammusu_dict)

    kammusu_data = []
    return []


def calc_kammusu_aa(td_tag) -> int:
    """艦娘の対空値を算出する
    """
    temp = td_tag.text
    if 'nil' in temp:
        return -1
    return int(temp)


def calc_kammusu_slot(td_tag):
    """艦娘の搭載数を算出する
    """

    # 搭載数を読み取る
    raw_slot = td_tag.text.replace("\n", '').split(',')
    slot_size = len(raw_slot)

    # 要素が空っぽだった場合の処理
    if slot_size == 1 and raw_slot[0] == '':
        return 0, [0, 0, 0, 0, 0]

    # 要素にイレギュラーな値が入っていた場合の処理
    if slot_size >= 1 and raw_slot[0] == '?':
        return -1, [0, 0, 0, 0, 0]

    # 搭載数をmapで計算(その過程で、NBSPとかいう害悪でしか無いクソ文字を削除している)
    slot = list(map(lambda x: int(x.replace("\xa0", '')), raw_slot))

    # 配列slotの要素が5つになるように調整
    for _ in range(0, 5 - slot_size):
        slot.append(0)

    return slot_size, slot


def calc_kammusu_weapon(td_tag, weapon_url_id_dict) -> int:
    result = [0, 0, 0, 0, 0]
    href_list = list(map(lambda x: x['href'], td_tag.select('a')))
    index = 0
    for href in href_list:
        if href in weapon_url_id_dict:
            result[index] = weapon_url_id_dict[href]
        index += 1
    return result


def crawl_enemy_kammusu_data() -> List[any]:
    """深海棲艦一覧をクロールして作成する
    """

    # 装備種一覧を読み込んでおく
    kammusu_type_dict, kammusu_type_wikia_dict = get_kammusu_type_dict()

    # まず、深海装備のURLとIDとの対応表を入手する
    weapon_url_id_dict = {}
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

            # URLを読み取る
            url = td_tag_list[2].select("a")[0]['href']
            weapon_url_id_dict[url] = id

    # 次に、深海棲艦のスペックを読み取って記録する
    kammusu_data = []
    with urllib.request.urlopen('http://kancolle.wikia.com/wiki/Enemy_Vessels/Full') as request:
        # 取得、パース
        soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')
        tr_tag_list = soup.select("div tr")

        # 1行づつ読み取っていく
        for trTag in tr_tag_list:
            # 関係ない行は無視する
            td_tag_list = trTag.select("td")
            if len(td_tag_list) < 20:
                continue

            # 艦船IDを読み取る
            id = int(td_tag_list[1].text)

            # 艦種を読み取る
            kammusu_type = kammusu_type_wikia_dict[td_tag_list[0].text.replace("\n", '').replace(' ', '')]

            # 艦名を読み取る
            name = td_tag_list[4].text.replace("\n", '').replace(' ', '')

            # 対空を読み取る
            aa = calc_kammusu_aa(td_tag_list[9])
            if aa < 0:
                continue

            # スロットを読み取る
            slot_size, slot = calc_kammusu_slot(td_tag_list[18])
            if slot_size < 0:
                continue

            # 艦種を補正する
            if kammusu_type == kammusu_type_wikia_dict['DD'] and 'PT' in name:
                kammusu_type = kammusu_type_wikia_dict['PT']
            if kammusu_type == kammusu_type_wikia_dict['BBV']:
                speed = int(td_tag_list[14].text)
                if speed == 0:
                    kammusu_type = kammusu_type_wikia_dict['AF']

            # 装備情報を読み取る
            weapon = calc_kammusu_weapon(td_tag_list[19], weapon_url_id_dict)

            data = (id, kammusu_type, name, aa, slot_size,
                    slot[0], slot[1], slot[2], slot[3], slot[4],
                    weapon[0], weapon[1], weapon[2], weapon[3], weapon[4],
                    0)
            kammusu_data.append(data)

    return kammusu_data


def crawl_kammusu_data() -> List[any]:
    """艦娘一覧をWebクロールして作成する
    """
    # 艦娘一覧を読み取る
    friend_kammusu_data = crawl_friend_kammusu_data_deckbuilder()

    # 深海棲艦一覧を読み取る
    enemy_kammusu_data = crawl_enemy_kammusu_data()

    # 合体させたものを戻り値とする
    kammusu_data = [(0, 0, 'なし', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)]
    kammusu_data.extend(friend_kammusu_data)
    kammusu_data.extend(enemy_kammusu_data)
    return kammusu_data


def create_kammusu_table(cursor) -> None:
    """ 艦娘テーブルを作成する
    """
    # 艦娘テーブルを作成する
    if has_table(cursor, 'kammusu'):
        cursor.execute('DROP TABLE kammusu')
    command = '''CREATE TABLE [kammusu] (
                [id] INTEGER NOT NULL UNIQUE,
                [type] INTEGER NOT NULL REFERENCES [kammusu_type]([id]),
                [name] TEXT NOT NULL,
                [aa] INTEGER NOT NULL,
                [slotsize] INTEGER NOT NULL,
                [slot1] INTEGER NOT NULL,
                [slot2] INTEGER NOT NULL,
                [slot3] INTEGER NOT NULL,
                [slot4] INTEGER NOT NULL,
                [slot5] INTEGER NOT NULL,
                [weapon1] INTEGER NOT NULL REFERENCES [weapon]([id]),
                [weapon2] INTEGER NOT NULL REFERENCES [weapon]([id]),
                [weapon3] INTEGER NOT NULL REFERENCES [weapon]([id]),
                [weapon4] INTEGER NOT NULL REFERENCES [weapon]([id]),
                [weapon5] INTEGER NOT NULL REFERENCES [weapon]([id]),
                [kammusu_flg] INTEGER NOT NULL,
                PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 艦娘テーブルにデータを追加する
    command = '''INSERT INTO kammusu (id, type, name, aa, slotsize,
                    slot1, slot2, slot3, slot4, slot5,
                    weapon1, weapon2, weapon3, weapon4, weapon5,
                    kammusu_flg) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    data = crawl_kammusu_data()
    cursor.executemany(command, data)

    # 艦娘テーブルにインデックスを設定する
    command = 'CREATE INDEX kammusu_name on kammusu(name)'
    cursor.execute(command)


def crawl_map_data() -> List[any]:
    """マップ一覧をWebクロールして作成する
    """

    map_data: List[any] = []
    for i in range(1, 8):
        with urllib.request.urlopen(f'http://kancolle.wikia.com/wiki/World_{i}') as request:
            # 取得、パース
            soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')

            # マップ名と対応するURLを取得
            event_div = soup.select('#EventTemplate')[0]
            li_list = event_div.select('ul > li')
            for li_tag in li_list:
                a_tag = li_tag.select('a')[0]
                map_link = f'http://kancolle.wikia.com{a_tag["href"]}'
                map_text = a_tag.text
                print(f'{map_text} - {map_link}')
                map_data.append([map_text, map_link])

    map_data2: List[any] = []
    for pair in map_data:
        # 各マップ画像のURLを取得
        image_url = ''
        root = lxml.html.parse(pair[1]).getroot()
        img_list = root.cssselect('img')
        for img_Tag in img_list:
            attributes = img_Tag.attrib
            if attributes.get('width') is None:
                continue
            if attributes.get('height') is None:
                continue
            if attributes.get('alt') is None:
                continue
            if int(attributes.get('width')) < 500:
                continue
            if not 'Map' in attributes['alt']:
                continue
            if attributes.get('data-src') is not None:
                image_url = attributes['data-src']
                break
            if attributes.get('src') is not None:
                image_url = attributes['src']
                break
        if image_url != '':
            image_url = re.sub('\.png.*', '.png', image_url)
            map_data2.append((pair[0], pair[1], image_url))
        print(f'{pair[0]} - {image_url}')
    return map_data2


def create_map_table(cursor) -> None:
    """ マップテーブルを作成する
    """
    # マップテーブルを作成する
    if has_table(cursor, 'map'):
        cursor.execute('DROP TABLE map')
    command = '''CREATE TABLE [map] (
                [name] TEXT NOT NULL UNIQUE,
                [info_url] TEXT NOT NULL UNIQUE,
                [image_url] TEXT NOT NULL UNIQUE,
                PRIMARY KEY([name]))'''
    cursor.execute(command)

    # マップテーブルにデータを追加する
    command = '''INSERT INTO map (name, info_url, image_url) VALUES (?,?,?)'''
    map_data = crawl_map_data()
    print(map_data)
    cursor.executemany(command, map_data)


# 当該Pythonファイルのディレクトリ
ROOT_DIRECTORY = os.path.dirname(__file__)

# データベースファイルの相対ファイルパス
DB_PATH = '../ACS-Server/src/main/webapp/WEB-INF/GameData_.db'
DB_PATH = 'GameData.db'

with closing(sqlite3.connect(os.path.join(ROOT_DIRECTORY, DB_PATH), isolation_level='EXCLUSIVE')) as connect:
    cursor = connect.cursor()
    cursor.execute('PRAGMA journal_mode=Memory')
    cursor.execute('PRAGMA synchronous = Off')

    # 装備種テーブルを作成する
    print('装備種テーブルを作成...')
    # create_weapon_type_table(cursor)

    # 装備カテゴリテーブルを作成する
    print('装備カテゴリテーブルを作成...')
    # create_weapon_category_table(cursor)

    # 装備テーブルを作成する
    print('装備テーブルを作成...')
    # create_weapon_table(cursor)

    # 艦種テーブルを作成する
    print('艦種テーブルを作成...')
    # create_kammusu_type_table(cursor)

    # 艦娘テーブルを作成する
    print('艦娘テーブルを作成...')
    # create_kammusu_table(cursor)

    # マップテーブルを作成する
    print('マップテーブルを作成...')
    create_map_table(cursor)

    connect.commit()
