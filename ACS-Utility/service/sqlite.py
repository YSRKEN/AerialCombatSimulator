import os
import sqlite3
from contextlib import closing
from typing import List, Tuple

from constant import OUTPUT_PATH
from service.i_database import DatabaseService


class SQLiteService(DatabaseService):
    def __init__(self):
        file_path = os.path.join(OUTPUT_PATH, 'GameData.db')
        self.connect = closing(sqlite3.connect(file_path))
        self.cursor: sqlite3.Cursor = self.connect.thing.cursor()

    def execute(self, query: str, parameter: Tuple = None) -> None:
        if parameter is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, parameter)

    def executemany(self, query: str, parameter: List[Tuple]) -> None:
        self.cursor.executemany(query, parameter)

    def commit(self):
        self.connect.thing.commit()
