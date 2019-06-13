from abc import ABCMeta, abstractmethod
from typing import List, Tuple


class DatabaseService(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, query: str, parameter: Tuple = None) -> None:
        """SQLクエリを実行する

        Parameters
        ----------
        query
            SQLクエリ
        parameter
            パラメーター(これが存在する際は、queryの埋める位置に?と書かれている)
        """
        pass

    @abstractmethod
    def executemany(self, query: str, parameter: List[Tuple]) -> None:
        """大量のSQLクエリを実行する

        Parameters
        ----------
        query
            SQLクエリ
        parameter
            パラメーター(これが存在する際は、queryの埋める位置に?と書かれている)
        """
        pass

    @abstractmethod
    def commit(self):
        """コミットを行う
        """
        pass
