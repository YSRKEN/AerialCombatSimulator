import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { RestApiService } from '../../service/rest-api.service';

@Component({
  selector: 'app-own-unit',
  templateUrl: './own-unit.component.html',
  styleUrls: ['./own-unit.component.scss']
})
export class OwnUnitComponent implements OnInit {
  /**
   * 最大搭載数を返す
   * @param kammusuNameValue 艦名
   */
  private getSlotSize(kammusuNameValue: string): string[] {
    const slotSize = ['0', '0', '0', '0', '0'];

    // 艦の情報を検索する
    const list = this.KammusuNameList.filter(pair => pair.value === kammusuNameValue);
    if (list.length === 0) {
      return slotSize;
    }
    const kammusuSlotInfo = list[0].slot;

    // 順次登録する
    for(let i = 0; i < kammusuSlotInfo.length; ++i){
      slotSize[i] = '' + kammusuSlotInfo[i];
    }
    return slotSize;
  }

  /**
   * スロット数を返す
   * @param kammusuNameValue 艦名
   */
  private getSlotCount(kammusuNameValue: string): number {
    // 艦の情報を検索する
    const list = this.KammusuNameList.filter(pair => pair.value === kammusuNameValue);
    if (list.length === 0) {
      return 0;
    }
    return list[0].slot.length;
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
  KammusuNameList: { "value": string, "name": string, "slot": number[] }[];

  /**
   * 最大搭載数
   */
  SlotSize: string[] = ['0', '0', '0', '0', '0'];

  /**
   * スロット数
   */
  SlotCount: number;

  constructor(private saveData: SaveDataService, private restApi: RestApiService) { }

  async ngOnInit() {
    // 艦種リストを初期化
    this.KammusuTypeList = (await this.restApi.getKammusuTypes(true))
      .map(v => {return {'value': '' + v.id, 'name': v.name}});
    
    // 艦名リストを初期化
    this.KammusuNameList = (await this.restApi.getKammusuNames(parseInt(this.KammusuTypeValue)))
      .map(v => {return {'value': '' + v.id, 'name': v.name, 'slot': v.slot}});
    this.KammusuNameList.unshift({'value': '0', 'name': 'なし', 'slot': []});

    // 搭載数リストを更新
    this.SlotSize = this.getSlotSize(this.KammusuNameValue);

    // スロット数を更新
    this.SlotCount = this.getSlotCount(this.KammusuNameValue);
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
   * 艦種
   */
  get KammusuTypeValue(): string {
    return this.saveData.loadString('own-unit.[' + this.index + '].kammusu_type', '0');
  }
  set KammusuTypeValue(value: string) {
    // 保存
    this.saveData.saveString('own-unit.[' + this.index + '].kammusu_type', value);

    // 艦名リストを更新
    this.restApi.getKammusuNames(parseInt(this.KammusuTypeValue))
      .then(value => {
        this.KammusuNameList = value.map(v => {return {'value': '' + v.id, 'name': v.name, 'slot': v.slot}});
        this.KammusuNameList.unshift({'value': '0', 'name': 'なし', 'slot': []});
        if (this.KammusuNameList.filter(pair => pair.value === this.KammusuNameValue).length === 0){
          this.KammusuNameValue = '0';
        }
      })
  }

  /**
   * 艦名
   */
  get KammusuNameValue(): string {
    return this.saveData.loadString('own-unit.[' + this.index + '].kammusu_name', '0');
  }
  set KammusuNameValue(value: string) {
    // 保存
    this.saveData.saveString('own-unit.[' + this.index + '].kammusu_name', value);

    // 搭載数リストを更新
    this.SlotSize = this.getSlotSize(this.KammusuNameValue);

    // スロット数を更新
    this.SlotCount = this.getSlotCount(this.KammusuNameValue);
  }
}
