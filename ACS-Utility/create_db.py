# -*- coding: utf-8 -*-

import os
import pandas
import sqlite3
from contextlib import closing
from typing import List

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

def crawl_weapon_data() -> List[any]:
    # スタブ
    return [
        (  0,  0, 'なし',         0, 0, 0),
        (  2,  1, '12.7cm連装砲', 0, 0, 0),
        ( 22,  7, '烈風',        10, 0, 0),
        ( 54, 13, '彩雲',         0, 2, 0),
        (168, 31, '九六式陸攻',    1, 0, 0),
        (176, 33, '三式戦 飛燕',   9, 0, 3),
    ]

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
                 PRIMARY KEY([id]))'''
    cursor.execute(command)

    # 装備テーブルにデータを追加する
    command = 'INSERT INTO weapon (id, type, name, aa, accuracy, interception) VALUES (?,?,?,?,?,?)'
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
