import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-own-data',
  templateUrl: './own-data.component.html',
  styleUrls: ['./own-data.component.scss']
})
export class OwnDataComponent implements OnInit {
  /**
   * 陣形一覧を返す
   * @param fleetType 編成の種類
   */
  private getFleetFormationList(fleetType: string): { "value": string, "name": string }[] {
    if (fleetType !== '連合'){
      return [
        {"value":"0", "name":"単縦陣"},
        {"value":"1", "name":"複縦陣"},
        {"value":"2", "name":"輪形陣"},
        {"value":"3", "name":"提携陣"},
        {"value":"4", "name":"単横陣"},
        {"value":"5", "name":"警戒陣"},
      ];
    }else{
      return [
        {"value":"4", "name":"第一警戒航行序列(対潜警戒)"},
        {"value":"1", "name":"第二警戒航行序列(前方警戒)"},
        {"value":"2", "name":"第三警戒航行序列(輪形陣)"},
        {"value":"0", "name":"第四警戒航行序列(戦闘隊形)"},
      ];
    }
  }

  /**
   * 艦隊の陣形一覧
   */
  FleetFormationList: { "value": string, "name": string }[];

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    this.FleetFormationList = this.getFleetFormationList(this.fleetTypeString);
  }

  /**
   * 陣形の種類を表す文字列
   */
  get fleetTypeString(): string{
    const fleetTypeInt = parseInt(this.FleetTypeValue);
    if (fleetTypeInt === 0) {
      return '通常';
    }else if(fleetTypeInt === 1){
      return '遊撃';
    }else{
      return '連合';
    }
  }

  /**
   * 編成の種類
   */
  get FleetTypeValue(): string {
    return this.saveData.loadString('own-data.fleet_type', '0');
  }
  set FleetTypeValue(value: string) {
    // 保存
    this.saveData.saveString('own-data.fleet_type', value);

    // 選択を切り替え
    this.FleetFormationList = this.getFleetFormationList(this.fleetTypeString);

    // 切替時の整合性を保つ処理
    if (this.FleetFormationList.filter(pair => pair.value === this.FleetFormationValue).length === 0){
      this.FleetFormationValue = '0';
    }
  }

  /**
   * 陣形の種類
   */
  get FleetFormationValue(): string {
    return this.saveData.loadString('own-data.fleet_formation', '0');
  }
  set FleetFormationValue(value: string) {
    this.saveData.saveString('own-data.fleet_formation', value);
  }
}
