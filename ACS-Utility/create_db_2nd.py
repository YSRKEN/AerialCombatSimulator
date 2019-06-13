from service.sqlite import SQLiteService
from service.weapon_type import WeaponTypeService


def main():
    # 装備種を読み込み、DBにダンプする
    dbs = SQLiteService()
    wts = WeaponTypeService(dbs)
    wts.dump_to_db()


if __name__ == '__main__':
    main()
