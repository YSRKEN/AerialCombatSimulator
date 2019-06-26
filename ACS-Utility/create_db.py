# -*- coding: utf-8 -*-

import os
import re
import urllib.request
from typing import List

import lxml.cssselect
import lxml.html
import pandas


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

    # マップテーブルを作成する
    print('マップテーブルを作成...')
    create_map_table(cursor)

    # 陣形カテゴリテーブルを作成する
    print('陣形カテゴリテーブルを作成...')
    create_formation_category_table(cursor)

    # マステーブルを作成する
    print('マステーブルを作成...')
    create_position_table(cursor)
