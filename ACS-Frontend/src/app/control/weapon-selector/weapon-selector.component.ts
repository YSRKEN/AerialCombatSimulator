import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { RestApiService } from 'src/app/service/rest-api.service';

@Component({
  selector: 'app-weapon-selector',
  templateUrl: './weapon-selector.component.html',
  styleUrls: ['./weapon-selector.component.scss']
})
export class WeaponSelectorComponent implements OnInit {

  /**
   * 装備種の辞書
   */
  private weaponTypeDict: { [key: number]: string; } = {};

  /**
   * 航空機とみなす装備種の辞書
   */
  private readonly airTypeSet: { [key: number]: boolean; } = {
    5: true,
    6: true,
    7: true,
    8: true,
    11: true,
  };

  /**
   * 偵察機とみなす装備種の辞書
   */
  private readonly searchTypeSet: { [key: number]: boolean; } = {
    8: true,
    11: true,
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
        typeValueList = [0, 5, 6, 7, 8, 11];
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
  private getWeaponNameList(weaponTypeValue: string): { "value": string, "name": string }[] {
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
        case "艦偵":
        return [
          { 'value': '0', 'name': 'なし' },
          { 'value': '54', 'name': '彩雲' },
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
   * 指定した搭載数を最大値とする搭載数リストを返す
   * @param slotSize 最大搭載数
   */
  private getSlotCountList(slotSize: string): { "value": string, "name": string }[] {
    const slotSizeInt = parseInt(slotSize);
    const result = [];
    for(let i = 0; i <= slotSizeInt; ++i){
      result.push({ 'value': '' + i, 'name': '' + i });
    }
    return result;
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
   * そのスロットにおける最大搭載数
   */
  @Input() set slotSize(value: string) {
    if (value === undefined || value === '') {
      value = '0';
    }
    this.SlotCountList = this.getSlotCountList(value);
    this.SlotCountValue = '' + (this.SlotCountList.length - 1);
  }

  /**
   * 装備種リスト
   */
  WeaponTypeList: { "value": string, "name": string }[];

  /**
   * 装備名リスト
   */
  WeaponNameList: { "value": string, "name": string }[];

  /**
   * 装備改修度リスト
   */
  WeaponRfList: { "value": string, "name": string }[] = [
    {"value":"0", "name":""},
    {"value":"1", "name":"☆1"},
    {"value":"2", "name":"☆2"},
    {"value":"3", "name":"☆3"},
    {"value":"4", "name":"☆4"},
    {"value":"5", "name":"☆5"},
    {"value":"6", "name":"☆6"},
    {"value":"7", "name":"☆7"},
    {"value":"8", "name":"☆8"},
    {"value":"9", "name":"☆9"},
    {"value":"10", "name":"☆max"},
  ];

  /**
   * 艦載機熟練度リスト
   */
  WeaponMasList: { "value": string, "name": string }[] = [
    {"value":"0", "name":""},
    {"value":"1", "name":"|"},
    {"value":"2", "name":"||"},
    {"value":"3", "name":"|||"},
    {"value":"4", "name":"/"},
    {"value":"5", "name":"//"},
    {"value":"6", "name":"///"},
    {"value":"7", "name":">>"},
    {"value":"8", "name":">>>"},
  ];

  /**
   * 搭載数リスト
   */
  SlotCountList: { "value": string, "name": string }[] = [
    { "value": '0', "name": '0' }
  ];

  constructor(private saveData: SaveDataService, private restApi: RestApiService) { }

  async ngOnInit() {
    // @Inputをチェックする
    if (this.prefix === undefined || undefined === '') {
      throw new Error("<app-weapon-selector>のprefix属性は省略できません。");
    }

    // 事前にAPIを叩いておく
    const weaponTypes = await this.restApi.getWeaponTypes();
    weaponTypes.forEach(pair => {
      this.weaponTypeDict[parseInt(pair.id)] = pair.name;
    });

    // 装備種リストを初期化
    this.WeaponTypeList = this.getWeaponTypeList(this.category);
    
    // 装備リストを初期化
    this.WeaponNameList = this.getWeaponNameList(this.WeaponTypeValue);

    // 搭載数リストを初期化
    // ('LBAS'はここで初期化されるが、そうでない場合は@Input() set slotSizeで初期化される)
    if (this.category === 'LBAS') {
      var maxSlotSize: string = this.searchTypeSet[parseInt(this.WeaponTypeValue)] ? '4' : '18';
      this.SlotCountList = this.getSlotCountList(maxSlotSize);
    }
  }

  /**
   * 装備種
   */
  get WeaponTypeValue(): string {
    return this.saveData.loadString(this.prefix + '.weapon_type', '0');
  }
  set WeaponTypeValue(value: string) {
    // 保存
    this.saveData.saveString(this.prefix + '.weapon_type', value);
    
    // 装備名一覧を更新
    this.WeaponNameList = this.getWeaponNameList(this.WeaponTypeValue);
    if (this.WeaponNameList.filter(pair => pair.value === this.WeaponNameValue).length === 0){
      this.WeaponNameValue = '0';
    }

    // 搭載数を更新
    if (this.category === 'LBAS') {
      var maxSlotSize: string = this.searchTypeSet[parseInt(this.WeaponTypeValue)] ? '4' : '18';
      this.SlotCountList = this.getSlotCountList(maxSlotSize);
    }
    this.SlotCountValue = '' + (this.SlotCountList.length - 1);
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

  /**
   * 装備改修度
   */
  get WeaponRfValue(): string {
    return this.saveData.loadString(this.prefix + '.weapon_rf', '0');
  }
  set WeaponRfValue(value: string) {
    this.saveData.saveString(this.prefix + '.weapon_rf', value);
  }

  /**
   * 艦載機熟練度
   */
  get WeaponMasValue(): string {
    return this.saveData.loadString(this.prefix + '.weapon_mas', '7');
  }
  set WeaponMasValue(value: string) {
    this.saveData.saveString(this.prefix + '.weapon_mas', value);
  }

  /**
   * 搭載数
   */
  get SlotCountValue(): string {
    return this.saveData.loadString(this.prefix + '.slot_count', '0');
  }
  set SlotCountValue(value: string) {
    this.saveData.saveString(this.prefix + '.slot_count', value);
  }

  get IsAirType(): boolean {
    return this.airTypeSet[parseInt(this.WeaponTypeValue)];
  }
}
