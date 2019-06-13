# -*- coding: utf-8 -*-

import json
import os
import re
import urllib.request
from typing import List, Dict

import lxml.cssselect
import lxml.html
import pandas
from bs4 import BeautifulSoup


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
    attack = int(status['Icon_Gun']) if 'Icon_Gun' in status else 0
    torpedo = int(status['Icon_Torpedo']) if 'Icon_Torpedo' in status else 0
    antisub = int(status['Icon_ASW']) if 'Icon_ASW' in status else 0
    bomber = int(status['Icon_Dive']) if 'Icon_Dive' in status else 0

    return aa, accuracy, interception, attack, torpedo, antisub, bomber


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
            aa, accuracy, interception, attack, torpedo, antisub, bomber = calc_weapon_status(td_tag_list[4])
            radius = weapon_radius_dict[name] if name in weapon_radius_dict else 0

            # 装備種を読み取る
            weapon_type = calc_weapon_type(td_tag_list[3], name, aa, weapon_type_default_dict, weapon_type_wikia_dict)

            # データを入力する
            aa = aa if aa >= 0 else 0
            weapon_data.append((id, weapon_type, name, aa, accuracy, interception, radius, 1, attack, torpedo, antisub,
                                bomber))
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
            aa, accuracy, interception, attack, torpedo, antisub, bomber = calc_weapon_status(td_tag_list[4])

            # 装備種を読み取る
            weapon_type = calc_weapon_type(td_tag_list[3], name, aa, weapon_type_default_dict, weapon_type_wikia_dict)

            # データを入力する
            aa = aa if aa >= 0 else 0
            weapon_data.append((id, weapon_type, name, aa, accuracy, 0, 0, 0, attack, torpedo, antisub, bomber))
    return weapon_data


def crawl_weapon_data() -> List[any]:
    """装備一覧をWebクロールして作成する
    """
    # 艦娘の装備一覧を読み取る
    friend_weapon_data = crawl_friend_weapon_data()

    # 深海棲艦の装備一覧を読み取る
    enemy_weapon_data = crawl_enemy_weapon_data()

    # 合体させたものを戻り値とする
    weapon_data = [(0, 0, 'なし', 0, 0, 0, 0, 1, 0, 0, 0, 0)]
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
                 [attack] INTEGER NOT NULL,
                 [torpedo] INTEGER NOT NULL,
                 [antisub] INTEGER NOT NULL,
                 [bomber] INTEGER NOT NULL,
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 装備テーブルにデータを追加する
    command = 'INSERT INTO weapon (id, type, name, aa, accuracy, interception, radius, for_kammusu_flg, attack,' \
              'torpedo, antisub, bomber) VALUES (?,?,?,?,?,?,?,?,?,?,?, ?)'
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
            aa = json_data['max_aac']

            # 火力
            attack = json_data['max_fire']

            # 雷装
            torpedo = json_data['max_torpedo']

            # 対潜
            antisub = json_data['max_ass']

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
                    1, attack, torpedo, antisub)
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


def calc_kammusu_weapon(td_tag, weapon_url_id_dict) -> List[int]:
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

            # 火力を読み取る
            attack = calc_kammusu_aa(td_tag_list[7])
            if attack < 0:
                continue

            # 雷装を読み取る
            torpedo = calc_kammusu_aa(td_tag_list[8])
            if torpedo < 0:
                continue

            # 対潜を読み取る
            antisub = calc_kammusu_aa(td_tag_list[11])

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
                    0, attack, torpedo, antisub)
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
    kammusu_data = [(0, 0, 'なし', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0)]
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
                [attack] INTEGER NOT NULL,
                [torpedo] INTEGER NOT NULL,
                [antisub] INTEGER NOT NULL,
                PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 艦娘テーブルにデータを追加する
    command = '''INSERT INTO kammusu (id, type, name, aa, slotsize,
                    slot1, slot2, slot3, slot4, slot5,
                    weapon1, weapon2, weapon3, weapon4, weapon5,
                    kammusu_flg, attack, torpedo, antisub) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    data = crawl_kammusu_data()
    cursor.executemany(command, data)

    # 艦娘テーブルにインデックスを設定する
    command = 'CREATE INDEX kammusu_name on kammusu(name)'
    cursor.execute(command)


def crawl_map_data() -> List[any]:
    """マップ一覧をWebクロールして作成する
    """

    map_data: List[any] = []
    # 通常海域
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
    # 限定海域
    with urllib.request.urlopen('https://kancolle.fandom.com/wiki/Events/Main') as res:
        html_text = res.read()
        with open('temp.html', 'wb') as f:
            f.write(html_text)
        page1: lxml.html.HtmlElement = lxml.html.fromstring(html_text)
        tr_list = page1.cssselect('tr')
        event_url = ''
        for record in tr_list:
            td_list = record.cssselect('td')
            if len(td_list) < 7:
                continue
            temp = td_list[0].cssselect('b')
            if len(temp) < 1:
                continue
            event_url = temp[0].cssselect('a')[0].attrib['href']
        event_url = f'https://kancolle.fandom.com{event_url}'

        with urllib.request.urlopen(event_url) as request:
            # 取得、パース
            soup: BeautifulSoup = BeautifulSoup(request.read(), 'html.parser')

            # マップ名と対応するURLを取得
            event_div = soup.select('#EventTemplate')[0]
            li_list = event_div.select('ul > li')
            for li_tag in li_list:
                a_tag = li_tag.select('a')[0]
                map_link = f'http://kancolle.wikia.com{a_tag["href"]}'
                map_text: str = a_tag.text
                if map_text[0:2] != 'E-':
                    continue
                print(f'{map_text} - {map_link}')
                map_data.append([map_text, map_link])

    map_data2: List[any] = []
    for pair in map_data:
        # 各マップ画像のURLを取得
        image_url = ''
        with urllib.request.urlopen(pair[1]) as f:
            html_text = f.read().decode('UTF-8')
            root = lxml.html.fromstring(html_text)
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
    cursor.executemany(command, map_data)


def crawl_position_data(cursor) -> List[any]:
    # マップ一覧を取得する
    map_list = cursor.execute('SELECT name, info_url FROM map')

    # 順番に読み取り、配列に記録する
    result: List[any] = []
    formation_image_alt_dict = {
        'LineAhead': 1,    # 単縦陣
        'DoubleLine': 2,   # 複縦陣
        'Diamond': 3,      # 輪形陣
        'Echelon': 4,      # 梯形陣
        'LineAbreast': 5,  # 単横陣
        'Formation 1': 15, # 第一警戒航行序列(対潜警戒)
        'Formation 2': 12, # 第二警戒航行序列(前方警戒)
        'Formation 3': 13, # 第三警戒航行序列(輪形陣)
        'Formation 4': 11, # 第四警戒航行序列(戦闘隊形)
    }
    formation_span_text_dict = {
        'Line Ahead': 1,  # 単縦陣
        'Double Line': 2,  # 複縦陣
        'Diamond': 3,  # 輪形陣
        'Echelon': 4,  # 梯形陣
        'Line Abreast': 5,  # 単横陣
        'Vanguard': 6,  # 警戒陣
        'CruisingFormation 1': 15,  # 第一警戒航行序列(対潜警戒)
        'CruisingFormation 2': 12,  # 第二警戒航行序列(前方警戒)
        'CruisingFormation 3': 13,  # 第三警戒航行序列(輪形陣)
        'CruisingFormation 4': 11,  # 第四警戒航行序列(戦闘隊形)
    }
    for map_data in map_list:
        map_name, map_url = map_data
        print(f'{map_name} - {map_url}')

        # パース
        with urllib.request.urlopen(map_url) as f:
            html_text = f.read().decode('UTF-8')
            root = lxml.html.fromstring(html_text)

            # 「マップのマスと敵編成一覧」情報を取り出す
            scrollable_div_list = root.cssselect('div.scrollable')
            scrollable_div_tag = None
            if len(scrollable_div_list) == 0:
                div_list = root.cssselect('div')
                for div_tag in div_list:
                    attributes = div_tag.attrib
                    style_attr = attributes.get('style')
                    if style_attr is None:
                        continue
                    if 'max-height:' not in style_attr:
                        continue
                    if 'overflow-y:auto' not in style_attr:
                        continue
                    if 'overflow-x:hidden' not in style_attr:
                        continue
                    scrollable_div_tag = div_tag
                    break
            else:
                scrollable_div_tag = scrollable_div_list[0]

            # 「マップのマスと敵編成一覧」をパースして順次代入する
            point_table_list = scrollable_div_tag.cssselect('table')
            for point_table_tag in point_table_list:
                # 戦闘しないテーブルは無視する
                th_text = ','.join(list(map(lambda x: x.text_content(), point_table_tag.cssselect('th'))))
                if 'Empty Node' in th_text:
                    continue
                if 'Resource Node' in th_text:
                    continue
                if 'Air Raids' in th_text:
                    continue

                # テーブルの中でtdを持つtr一覧を取得し、マス名と敵編成を読み取る
                tr_list = point_table_tag.cssselect('tr')
                point_name = ''
                pattern_index = 1
                first_flg = True
                for tr_tag in tr_list:
                    # tdを持たないtrは無視する
                    td_list = tr_tag.cssselect('td')
                    if len(td_list) == 0:
                        continue

                    # 最初のtrは、tdとしてマス名を含むので取得する
                    if first_flg:
                        point_name = td_list[0].text_content().replace("\n", '')

                    # 敵編成が記録されているtdの位置を判断する
                    temp_index = -1
                    for i in range(0, len(td_list)):
                        if len(td_list[i].cssselect('a.link-internal')) > 0:
                            temp_index = i
                            break
                    if temp_index == -1:
                        continue

                    # 余計なタグを削除する
                    span_span_list = td_list[temp_index].cssselect('span > span')
                    for span_tag in span_span_list:
                        span_tag.drop_tree()

                    # 敵編成を読み取る
                    a_list = td_list[temp_index].cssselect('a.link-internal')
                    enemy_list = []
                    for a_tag in a_list:
                        attributes = a_tag.attrib
                        enemy_id = int(re.sub(r'.*\((\d+)\):.*', r'\1', attributes.get('title')))
                        enemy_list.append(enemy_id)

                    # ラスダンで編成が変わる場合の対策
                    td_text = ','.join(list(map(lambda x: x.text_content(), td_list)))
                    final_flg = '(Final)' in td_text

                    # 敵の陣形を読み取る
                    print(f'{point_name}-{pattern_index}-{final_flg}-{enemy_list}')
                    temp = td_list[1 if first_flg else 0].cssselect('img')
                    if len(temp) > 0:
                        formation_image_tag = td_list[1 if first_flg else 0].cssselect('img')[0]
                        attributes = formation_image_tag.attrib
                        formation_image_alt = attributes.get('alt')
                        formation_index = formation_image_alt_dict[formation_image_alt]
                    else:
                        formation_span_tag = td_list[1 if first_flg else 0].cssselect('span')[0]
                        formation_span_text = formation_span_tag.text_content()
                        formation_index = formation_span_text_dict[formation_span_text]

                    # 読み取った敵編成を登録する
                    for i in range(0, len(enemy_list)):
                        unit_data = (
                            map_name,
                            f'{point_name}-{pattern_index}',
                            i,
                            final_flg,
                            formation_index,
                            enemy_list[i]
                        )
                        result.append(unit_data)

                    # 次のループに向けた処理
                    if first_flg:
                        first_flg = False
                    pattern_index += 1

    return result


def create_position_table(cursor) -> None:
    """ マステーブルを作成する
    """
    # マステーブルを作成する
    if has_table(cursor, 'position'):
        cursor.execute('DROP TABLE position')
    command = '''CREATE TABLE [position] (
                [map] TEXT REFERENCES [map]([name]),
                [name] TEXT,
                [unit_index] INTEGER NOT NULL,
                [final_flg] INTEGER NOT NULL,
                [formation] INTEGER REFERENCES [formation_category]([id]),
                [enemy] INTEGER REFERENCES [kammusu]([id]),
                PRIMARY KEY([map],[name],[unit_index]))'''
    cursor.execute(command)

    # マステーブルにデータを追加する
    command = '''INSERT INTO position (map, name, unit_index, final_flg, formation, enemy) VALUES (?,?,?,?,?,?)'''
    map_data = crawl_position_data(cursor)
    cursor.executemany(command, map_data)


def create_formation_category_table(cursor) -> None:
    """ 陣形カテゴリテーブルを作成する
    """
    # 陣形カテゴリテーブルを作成する
    if has_table(cursor, 'formation_category'):
        cursor.execute('DROP TABLE formation_category')
    command = '''CREATE TABLE [formation_category] (
                [id] INTEGER NOT NULL UNIQUE,
                [category] TEXT NOT NULL,
                PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 陣形カテゴリテーブルにデータを追加する
    command = 'INSERT INTO formation_category (id, category) VALUES (?,?)'
    formation_category_df = pandas.read_csv(os.path.join(ROOT_DIRECTORY, 'formation_category.csv'))
    data = list(map(lambda x: (x[0], x[1]), formation_category_df.values))
    cursor.executemany(command, data)
    connect.commit()
    # 装備テーブルを作成する
    print('装備テーブルを作成...')
    create_weapon_table(cursor)

    # 艦種テーブルを作成する
    print('艦種テーブルを作成...')
    create_kammusu_type_table(cursor)

    # 艦娘テーブルを作成する
    print('艦娘テーブルを作成...')
    create_kammusu_table(cursor)

    # マップテーブルを作成する
    print('マップテーブルを作成...')
    create_map_table(cursor)

    # 陣形カテゴリテーブルを作成する
    print('陣形カテゴリテーブルを作成...')
    create_formation_category_table(cursor)

    # マステーブルを作成する
    print('マステーブルを作成...')
    create_position_table(cursor)

    connect.commit()
