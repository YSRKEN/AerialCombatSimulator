import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-own-unit',
  templateUrl: './own-unit.component.html',
  styleUrls: ['./own-unit.component.scss']
})
export class OwnUnitComponent implements OnInit {
  /**
   * 艦種リストを返す
   */
  private getKammusuTypeList(): { "value": string, "name": string }[] {
    return [
      { "value": "0", "name": "なし" },
      { "value": "2", "name": "駆逐艦" },
      { "value": "7", "name": "軽空母" },
      { "value": "11", "name": "正規空母" },
    ];
  }

  /**
   * 艦名リストを返す
   */
  private getKammusuNameList(type: string): { "value": string, "name": string }[] {
    switch (type) {
    case '2':
      return [
        { "value": "0", "name": "なし" },
        { "value": "9", "name": "吹雪" },
        { "value": "10", "name": "白雪" },
        { "value": "11", "name": "深雪" },
        { "value": "32", "name": "初雪" },
      ];
    case '7':
      return [
        { "value": "0", "name": "なし" },
        { "value": "89", "name": "鳳翔" },
      ];
    case '11':
      return [
        { "value": "0", "name": "なし" },
        { "value": "196", "name": "飛龍改二" },
        { "value": "197", "name": "蒼龍改二" },
        { "value": "277", "name": "赤城改" },
        { "value": "278", "name": "加賀改" },
      ];
    default:
      return [
        { "value": "0", "name": "なし" }
      ];
    }
  }

  /**
   * 艦隊の番号
   */
  @Input() index: string = '1';

  /**
   * 艦隊の種類
   */
  @Input() type: string = '0';

  /**
   * 艦種一覧
   */
  KammusuTypeList: { "value": string, "name": string }[];

  /**
   * 艦名一覧
   */
  KammusuNameList: { "value": string, "name": string }[];

  /**
   * 艦種
   */
  get KammusuTypeValue(): string {
    return this.saveData.loadString('own-unit.[' + this.index + '].kammusu_type', '0');
  }
  set KammusuTypeValue(value: string) {
    // 保存
    this.saveData.saveString('own-unit.[' + this.index + '].kammusu_type', value);

    // 艦名リストを更新
    this.KammusuNameList = this.getKammusuNameList(this.KammusuTypeValue);
    if (this.KammusuNameList.filter(pair => pair.value === this.KammusuNameValue).length === 0){
      this.KammusuNameValue = '0';
    }
  }

  /**
   * 艦名
   */
  get KammusuNameValue(): string {
    return this.saveData.loadString('own-unit.[' + this.index + '].kammusu_name', '0');
  }
  set KammusuNameValue(value: string) {
    this.saveData.saveString('own-unit.[' + this.index + '].kammusu_name', value);
  }

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    // 艦種リストを初期化
    this.KammusuTypeList = this.getKammusuTypeList();
    
    // 艦名リストを初期化
    this.KammusuNameList = this.getKammusuNameList(this.KammusuTypeValue);
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
}
