import time

from service.http import HttpService
from service.i_dom import DomService
from service.kammusu import KammusuService
from service.kammusu_type import KammusuTypeService
from service.lxml_dom import LxmlDomService
from service.sqlite import SQLiteService
from service.weapon import WeaponService
from service.weapon_category import WeaponCategoryService
from service.weapon_type import WeaponTypeService


def main():
    # データベースを初期化
    print('データベースを初期化...')
    dbs = SQLiteService()

    # 装備種を読み込み、DBにダンプする
    print('装備種を読み込み、DBにダンプ...')
    wts = WeaponTypeService(dbs)
    wts.dump_to_db()

    # 装備カテゴリを読み込み、DBにダンプする
    print('装備カテゴリを読み込み、DBにダンプ...')
    wcs = WeaponCategoryService(dbs)
    wcs.dump_to_db()

    # 装備を読み込み、DBにダンプする
    print('装備を読み込み、DBにダンプ...')
    https = HttpService()
    doms: DomService = LxmlDomService(https)
    ws = WeaponService(dbs, doms, wts, wcs)
    print('  艦娘の装備を読み込み...')
    ws.crawl_for_kammusu()
    print('  深海棲艦の装備を読み込み...')
    ws.crawl_for_enemy()
    print('  DBにダンプ...')
    ws.dump_to_db()

    # 艦種を読み込み、DBにダンプする
    print('艦種を読み込み、DBにダンプ...')
    kts = KammusuTypeService(dbs)
    kts.dump_to_db()

    # 艦娘を読み込み、DBにダンプする
    print('艦娘を読み込み、DBにダンプ...')
    ks = KammusuService(dbs, doms, https, kts)
    print('  艦娘を読み込み...')
    ks.crawl_kammusu()
    print('  深海棲艦を読み込み...')
    ks.crawl_enemy()
    print('  DBにダンプ...')
    ks.dump_to_db()

    print('完了.')


if __name__ == '__main__':
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    print(f'{elapsed_time}[s]')

# キャッシュ前→162.6[s]
# キャッシュ後→4.8[s]
