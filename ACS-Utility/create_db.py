# -*- coding: utf-8 -*-

import os
import re
import urllib.request
from typing import List

import lxml.cssselect
import lxml.html
import pandas
from bs4 import BeautifulSoup


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
