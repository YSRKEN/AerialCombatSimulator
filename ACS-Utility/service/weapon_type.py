import os

import pandas

from constant import DATA_PATH
from model.weapon_type import WeaponType


class WeaponTypeService:
    """装備種を検索するためのサービスクラス
    """

    def __init__(self):
        self.df = pandas.read_csv(os.path.join(DATA_PATH, 'weapon_type.csv'))

    def find_by_wikia_name(self, key: str) -> WeaponType:
        """Wikiaにおける登録名から装備種情報を検索する
            (ヒットしない場合は「その他」扱いにする)

        Parameters
        ----------
        key
            Wikiaにおける登録名

        Returns
        -------
            装備種情報
        """
        result = self.df.query(f"wikia_name == '{key}'")
        if len(result) == 0:
            return self.find_by_wikia_name('Other')
        temp = result.to_dict(orient='records')[0]
        return WeaponType(**temp)
