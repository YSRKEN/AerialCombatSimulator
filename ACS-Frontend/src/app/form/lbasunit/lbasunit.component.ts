import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-lbasunit',
  templateUrl: './lbasunit.component.html',
  styleUrls: ['./lbasunit.component.scss']
})
export class LBASUnitComponent implements OnInit {

  /**
   * スロット数
   */
  readonly WEAPON_COUNT: number = 4;

  /**
   * 基地航空隊の状態一覧
   */
  LBASCountList: { "value": string, "name": string }[] = [
    {"value":"0", "name":"なし"},
    {"value":"1", "name":"分散"},
    {"value":"2", "name":"集中"},
  ];

  /**
   * 選択している状態
   */
  LBASCount: string;

  /**
   * 装備一覧
   */
  WeaponList: { "value": string, "name": string }[] = [
    {"value":"0", "name":"なし"},
    {"value":"22", "name":"烈風"},
    {"value":"52", "name":"流星改"},
    {"value":"54", "name":"彩雲"},
    {"value":"57", "name":"彗星一二型甲"},
  ];

  /**
   * 選択している装備
   */
  SelectedWeapon: string[] = ['','','',''];

  /**
   * 艦載機熟練度一覧
   */
  MasList: { "value": string, "name": string }[] = [
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
   * 選択している艦載機熟練度
   */
  WeaponMas: string[] = ['','','',''];

  /**
   * 装備改修度一覧
   */
  RfList: { "value": string, "name": string }[] = [
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
   * 選択している装備改修度
   */
  WeaponRf: string[] = ['','','',''];

  /**
   * 基地航空隊の機数一覧
   */
  SlotCountList: { "value": string, "name": string }[][] = [];

  /**
   * 選択している機数
   */
  SlotCount: string[] = ['','','',''];

  /**
   * 基地航空隊の番号
   */
  @Input() index: string = '1';
  IndexString: string;

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    // 基地航空隊の番号を設定
    const indexToString = {'1': '一', '2': '二', '3': '三'};
    this.IndexString = '第' + indexToString[this.index] + '航空隊';

    /**
     * 設定を読み込む
     */
    this.LBASCount = this.saveData.loadString('lbasunit.lbas_count' + this.index, '0');
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.SelectedWeapon[i] = this.saveData.loadString('lbasunit.selected_weapon_' + this.index + '' + (i + 1), '22');
    }
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.WeaponMas[i] = this.saveData.loadString('lbasunit.weapon_mas_' + this.index + '' + (i + 1), '7');
    }
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.WeaponRf[i] = this.saveData.loadString('lbasunit.weapon_rf_' + this.index + '' + (i + 1), '0');
    }
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.SlotCount[i] = this.saveData.loadString('lbasunit.slot_count_' + this.index + '' + (i + 1), '18');
    }

    // 機数を設定
    for(let i = 0; i < this.WEAPON_COUNT; ++i){
      this.calcSlotCountList(i, false);
    }
  }

  /**
   * 基地航空隊の状態を切り替えた際の処理
   * @param event 
   */
  changeLBASCount(event: any){
    this.LBASCount = event;
    this.saveData.saveString('lbasunit.lbas_count' + this.index, this.LBASCount);
  }

  /**
   * 装備の選択を切り替えた際の処理
   * @param event 
   */
  changeSelectedWeapon(event: any, index: number){
    this.SelectedWeapon[index] = event;
    this.saveData.saveString('lbasunit.selected_weapon_' + this.index + '' + (index + 1), this.SelectedWeapon[index]);
    this.calcSlotCountList(index);
  }

  /**
   * 艦載機熟練度の選択を切り替えた際の処理
   * @param event 
   */
  changeWeaponMas(event: any, index: number){
    this.WeaponMas[index] = event;
    this.saveData.saveString('lbasunit.weapon_mas_' + this.index + '' + (index + 1), this.WeaponMas[index]);
  }

  /**
   * 装備改修度の選択を切り替えた際の処理
   * @param event 
   */
  changeWeaponRf(event: any, index: number){
    this.WeaponRf[index] = event;
    this.saveData.saveString('lbasunit.weapon_rf_' + this.index + '' + (index + 1), this.WeaponRf[index]);
  }

  /**
   * 搭載数の選択を切り替えた際の処理
   * @param event 
   */
  changeSlotCount(event: any, index: number){
    this.SlotCount[index] = event;
    this.saveData.saveString('lbasunit.slot_count_' + this.index + '' + (index + 1), this.SlotCount[index]);
  }

  /**
   * 艦載機の搭載数の上限を動的に決定する
   * @param index 当該スロットのインデックス
   */
  calcSlotCountList(index: number, resetSlotCountFlg = true){
    // 最大搭載数を計算
    const MAX_SLOTCOUNT = 18;
    let maxSlotCount = MAX_SLOTCOUNT;
    if(this.SelectedWeapon[index] === '0'){
      maxSlotCount = 0;
    }else if(this.SelectedWeapon[index] === '54'){
      maxSlotCount = 4;
    }

    // 最大搭載数に従い、スロットの容量を計算
    this.SlotCountList[index] = [];
    for(let i = 0; i <= maxSlotCount; ++i){
      this.SlotCountList[index].push({"value":i.toString(), "name":i.toString()});
    }

    // 現在の搭載数を変更
    if (resetSlotCountFlg){
      this.changeSlotCount((this.SlotCountList[index].length - 1).toString(), index);
    }
  }
}
