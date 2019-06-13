from service.weapon_type import WeaponTypeService


def main():
    wts = WeaponTypeService()
    print(wts.find_by_wikia_name('Torpedo'))
    print(wts.find_by_wikia_name('hoge'))


if __name__ == '__main__':
    main()
