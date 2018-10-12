import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-own-unit',
  templateUrl: './own-unit.component.html',
  styleUrls: ['./own-unit.component.scss']
})
export class OwnUnitComponent implements OnInit {

  /**
   * スロット数
   */
  readonly WEAPON_COUNT: number = 5;

  /**
   * 艦隊の番号
   */
  @Input() index: string = '1';

  /**
   * 艦隊の種類
   */
  @Input() type: string = '0';

  /**
   * 艦娘の種類一覧
   */
  KammusuTypeList: { "value": string, "name": string }[] = [
    { "value": "0", "name": "なし" },
    { "value": "2", "name": "駆逐艦" },
    { "value": "7", "name": "軽空母" },
    { "value": "11", "name": "正規空母" },
  ];

  /**
   * 選択している装備
   */
  KammusuType: string;

  /**
   * 艦娘一覧
   */
  KammusuNameList: { "value": string, "name": string }[] = [
    { "value": "0", "name": "なし" },
    { "value": "196", "name": "飛龍改二" },
    { "value": "197", "name": "蒼龍改二" },
    { "value": "277", "name": "赤城改" },
    { "value": "278", "name": "加賀改" },
  ];

  /**
   * 選択している装備
   */
  KammusuName: string;

  /**
   * 装備一覧
   */
  WeaponList: { "value": string, "name": string }[] = [
    { "value": "0", "name": "なし" },
    { "value": "22", "name": "烈風" },
    { "value": "52", "name": "流星改" },
    { "value": "54", "name": "彩雲" },
    { "value": "57", "name": "彗星一二型甲" },
  ];

  /**
   * 選択している装備
   */
  SelectedWeapon: string[] = ['', '', '', '', ''];

  /**
   * 艦載機熟練度一覧
   */
  MasList: { "value": string, "name": string }[] = [
    { "value": "0", "name": "" },
    { "value": "1", "name": "|" },
    { "value": "2", "name": "||" },
    { "value": "3", "name": "|||" },
    { "value": "4", "name": "/" },
    { "value": "5", "name": "//" },
    { "value": "6", "name": "///" },
    { "value": "7", "name": ">>" },
    { "value": "8", "name": ">>>" },
  ];

  /**
   * 選択している艦載機熟練度
   */
  WeaponMas: string[] = ['', '', '', '', ''];

  /**
   * 装備改修度一覧
   */
  RfList: { "value": string, "name": string }[] = [
    { "value": "0", "name": "" },
    { "value": "1", "name": "☆1" },
    { "value": "2", "name": "☆2" },
    { "value": "3", "name": "☆3" },
    { "value": "4", "name": "☆4" },
    { "value": "5", "name": "☆5" },
    { "value": "6", "name": "☆6" },
    { "value": "7", "name": "☆7" },
    { "value": "8", "name": "☆8" },
    { "value": "9", "name": "☆9" },
    { "value": "10", "name": "☆max" },
  ];

  /**
   * 選択している装備改修度
   */
  WeaponRf: string[] = ['', '', '', '', ''];

  /**
   * 基地航空隊の機数一覧
   */
  SlotCountList: { "value": string, "name": string }[][] = [];

  /**
   * 選択している機数
   */
  SlotCount: string[] = ['', '', '', '', ''];

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    /**
     * 設定を読み込む
     */
    this.KammusuType = this.saveData.loadString('own-unit.kammusu_type' + this.index, '0');
    this.KammusuName = this.saveData.loadString('own-unit.kammusu_name' + this.index, '0');
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.SelectedWeapon[i] = this.saveData.loadString('own-unit.selected_weapon_' + this.index + '' + (i + 1), '0');
    }
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.WeaponMas[i] = this.saveData.loadString('own-unit.weapon_mas_' + this.index + '' + (i + 1), '7');
    }
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.WeaponRf[i] = this.saveData.loadString('own-unit.weapon_rf_' + this.index + '' + (i + 1), '0');
    }
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.SlotCount[i] = this.saveData.loadString('own-unit.slot_count_' + this.index + '' + (i + 1), '0');
    }
    this.changeKammusuType(this.KammusuType);
    this.changeKammusuName(this.KammusuName);

    // 機数を設定
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.calcSlotCountList(i, false);
    }
  }

  /**
   * 「X番艦」といった指標を表示
   */
  get UnitString(): string {
    if (parseInt(this.type) < 2) {
      return this.index + '番艦';
    } else {
      const indexInt = parseInt(this.index) - 1;
      return '第' + (Math.floor(indexInt / 6) + 1) + '艦隊 ' + ((indexInt % 6) + 1).toString() + '番艦';
    }
  }

  /**
   * 艦種を切り替えた際の処理
   * @param event 
   */
  changeKammusuType(event: any) {
    // 選択を保存
    this.KammusuType = event;
    this.saveData.saveString('own-unit.kammusu_type' + this.index, this.KammusuType);

    // 艦名一覧を切り替え(仮コード)
    switch (this.KammusuType) {
    case '0':
      this.KammusuNameList = [
        { "value": "0", "name": "なし" }
      ];
      break;
    case '2':
      this.KammusuNameList = [
        { "value": "0", "name": "なし" },
        { "value": "9", "name": "吹雪" },
        { "value": "10", "name": "白雪" },
        { "value": "11", "name": "深雪" },
        { "value": "32", "name": "初雪" },
      ];
      break;
    case '7':
      this.KammusuNameList = [
        { "value": "0", "name": "なし" },
        { "value": "89", "name": "鳳翔" },
      ];
      break;
    case '11':
      this.KammusuNameList = [
        { "value": "0", "name": "なし" },
        { "value": "196", "name": "飛龍改二" },
        { "value": "197", "name": "蒼龍改二" },
        { "value": "277", "name": "赤城改" },
        { "value": "278", "name": "加賀改" },
      ];
      break;
    }
    if (this.KammusuNameList.filter(pair => pair.value === this.KammusuName).length === 0){
      this.changeKammusuName('0');
    }
  }

  /**
   * 艦名を切り替えた際の処理
   * @param event 
   */
  changeKammusuName(event: any) {
    this.KammusuName = event;
    this.saveData.saveString('own-unit.kammusu_name' + this.index, this.KammusuName);
  }

  /**
 * 装備の選択を切り替えた際の処理
 * @param event 
 */
  changeSelectedWeapon(event: any, index: number) {
    this.SelectedWeapon[index] = event;
    this.saveData.saveString('own-unit.selected_weapon_' + this.index + '' + (index + 1), this.SelectedWeapon[index]);
    this.calcSlotCountList(index);
  }

  /**
   * 艦載機熟練度の選択を切り替えた際の処理
   * @param event 
   */
  changeWeaponMas(event: any, index: number) {
    this.WeaponMas[index] = event;
    this.saveData.saveString('own-unit.weapon_mas_' + this.index + '' + (index + 1), this.WeaponMas[index]);
  }

  /**
   * 装備改修度の選択を切り替えた際の処理
   * @param event 
   */
  changeWeaponRf(event: any, index: number) {
    this.WeaponRf[index] = event;
    this.saveData.saveString('own-unit.weapon_rf_' + this.index + '' + (index + 1), this.WeaponRf[index]);
  }

  /**
   * 搭載数の選択を切り替えた際の処理
   * @param event 
   */
  changeSlotCount(event: any, index: number) {
    this.SlotCount[index] = event;
    this.saveData.saveString('own-unit.slot_count_' + this.index + '' + (index + 1), this.SlotCount[index]);
  }

  /**
   * 艦載機の搭載数の上限を動的に決定する
   * @param index 当該スロットのインデックス
   */
  calcSlotCountList(index: number, resetSlotCountFlg = true){
    // 最大搭載数を計算して追加(仮コード)
    this.SlotCountList[index] = [];
    for(let i = 0; i <= 3; ++i){
      this.SlotCountList[index].push({"value":i.toString(), "name":i.toString()});
    }

    // 現在の搭載数を変更
    if (resetSlotCountFlg){
      this.changeSlotCount((this.SlotCountList[index].length - 1).toString(), index);
    }
  }
}
