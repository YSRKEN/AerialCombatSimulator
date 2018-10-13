import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-weapon-selector',
  templateUrl: './weapon-selector.component.html',
  styleUrls: ['./weapon-selector.component.scss']
})
export class WeaponSelectorComponent implements OnInit {

  /**
   * 装備種の辞書
   */
  private readonly weaponTypeDict: { [key: string]: string; } = {
    0: "なし",
    1: "主砲",
    2: "副砲",
    3: "魚雷",
    5: "艦戦",
    6: "艦爆",
    7: "艦攻",
    8: "艦偵",
    11: "水偵",
  };

  /**
   * 装備種カテゴリに対応した装備種リストを返す
   * @param category 装備種カテゴリ
   */
  private getWeaponTypeList(category: string): { "value": string, "name": string }[] {
    // 装備種のkeyの一覧を取得する
    let typeValueList = [];
    switch (category) {
      case 'LBAS':
        typeValueList = [0, 5, 6, 7, 8];
        break;
      case 'Normal':
        typeValueList = [0, 1, 2, 3, 5, 6, 7, 8, 11];
        break;
      default:
        typeValueList = [0];
        break;
    }

    // 装備種の一覧を作成する
    return typeValueList.map(v => {
      return { 'value': '' + v, 'name': this.weaponTypeDict[v] };
    });
  }

  /**
   * 装備種に対応した装備リストを返す
   * @param weaponTypeValue 装備種
   */
  private getWeaponNameList(weaponTypeValue: string) {
    switch (this.weaponTypeDict[parseInt(weaponTypeValue)]) {
      case "主砲":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '2', 'name': '12.7cm連装砲' },
          { 'value': '6', 'name': '20.3cm連装砲' },
          { 'value': '7', 'name': '35.6cm連装砲' },
        ];
      case "副砲":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '11', 'name': '15.2cm単装砲' },
        ];
      case "魚雷":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '13', 'name': '61cm三連装魚雷' },
        ];
        case "艦戦":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '19', 'name': '九六式艦戦' },
          { 'value': '22', 'name': '烈風' },
        ];
        case "艦爆":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '23', 'name': '九九式艦爆' },
          { 'value': '57', 'name': '彗星一二型甲' },
        ];
        case "艦攻":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '16', 'name': '九七式艦攻' },
          { 'value': '52', 'name': '流星改' },
        ];
        case "水偵":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '25', 'name': '零式水上偵察機' },
        ];
      default:
        return [
          { 'value': '0', 'name': 'なし' },
        ];
    }
  }

  /**
   * 装備種カテゴリ
   * 'LBAS' => 基地航空隊の装備だけ表示する
   * 'Normal' => 全ての装備を表示する
   * その他 => どの装備も表示しない
   */
  @Input() category: string;

  /**
   * 保存時のキーに付ける接頭辞
   */
  @Input() prefix: string;

  /**
   * 装備種リスト
   */
  WeaponTypeList: { "value": string, "name": string }[];

  /**
   * 装備名リスト
   */
  WeaponNameList: { "value": string, "name": string }[];

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    // @Inputをチェックする
    if (this.prefix === undefined || undefined === '') {
      throw new Error("<app-weapon-selector>のprefix属性は省略できません。");
    }

    // 装備種リストを初期化
    this.WeaponTypeList = this.getWeaponTypeList(this.category);
    
    // 装備リストを初期化
    this.WeaponNameList = this.getWeaponNameList(this.WeaponTypeValue);
  }

  /**
   * 装備種
   */
  get WeaponTypeValue(): string {
    return this.saveData.loadString(this.prefix + '.weapon_type', '0');
  }
  set WeaponTypeValue(value: string) {
    this.saveData.saveString(this.prefix + '.weapon_type', value);
    this.WeaponNameList = this.getWeaponNameList(this.WeaponTypeValue);
  }

  /**
   * 装備名
   */
  get WeaponNameValue(): string {
    return this.saveData.loadString(this.prefix + '.weapon_name', '0');
  }
  set WeaponNameValue(value: string) {
    this.saveData.saveString(this.prefix + '.weapon_name', value);
  }
}
