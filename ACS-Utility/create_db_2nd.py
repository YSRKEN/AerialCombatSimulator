from service.sqlite import SQLiteService
from service.weapon_category import WeaponCategoryService
from service.weapon_type import WeaponTypeService


def main():
    # データベースを初期化
    dbs = SQLiteService()

    # 装備種を読み込み、DBにダンプする
    wts = WeaponTypeService(dbs)
    wts.dump_to_db()

    # 装備カテゴリを読み込み、DBにダンプする
    wcs = WeaponCategoryService(dbs)
    wcs.dump_to_db()


if __name__ == '__main__':
    main()
