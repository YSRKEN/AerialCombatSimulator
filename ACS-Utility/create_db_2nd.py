from service.http import HttpService
from service.i_dom import DomService
from service.lxml_dom import LxmlDomService
from service.sqlite import SQLiteService
from service.weapon import WeaponService
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

    # 装備を読み込み、DBにダンプする
    https = HttpService()
    doms: DomService = LxmlDomService(https)
    ws = WeaponService(dbs, doms, wts, wcs)
    ws.crawl_for_kammusu()
    ws.crawl_for_enemy()
    ws.dump_to_db()


if __name__ == '__main__':
    main()
