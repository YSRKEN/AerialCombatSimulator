import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-own-data',
  templateUrl: './own-data.component.html',
  styleUrls: ['./own-data.component.scss']
})
export class OwnDataComponent implements OnInit {

  FleetType: string;

  /**
   * 艦隊の陣形一覧
   */
  FleetFormationList: { "value": string, "name": string }[];

  FleetFormation: string;

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    this.FleetType = this.saveData.loadString('own-data.fleet_type', '0');
    this.FleetFormation = this.saveData.loadString('own-data.fleet_formation', '0');
    this.changeFleetType(this.FleetType);
  }

  /**
   * 搭載数の選択を切り替えた際の処理
   * @param event 
   */
  changeFleetType(event: any){
    // 入力を保存
    this.FleetType = event;
    this.saveData.saveString('own-data.fleet_type', this.FleetType);

    // 選択を切り替え
    if (this.fleetTypeString !== '連合'){
      this.FleetFormationList = [
        {"value":"0", "name":"単縦陣"},
        {"value":"1", "name":"複縦陣"},
        {"value":"2", "name":"輪形陣"},
        {"value":"3", "name":"提携陣"},
        {"value":"4", "name":"単横陣"},
        {"value":"5", "name":"警戒陣"},
      ];
    }else{
      this.FleetFormationList = [
        {"value":"4", "name":"第一警戒航行序列(対潜警戒)"},
        {"value":"1", "name":"第二警戒航行序列(前方警戒)"},
        {"value":"2", "name":"第三警戒航行序列(輪形陣)"},
        {"value":"0", "name":"第四警戒航行序列(戦闘隊形)"},
      ];
    }
    if (this.FleetFormationList.filter(pair => pair.value === this.FleetFormation).length === 0){
      this.changeFleetFormation('0');
    }
  }

  /**
   * 陣形を切り替えた際の処理
   * @param event 
   */
  changeFleetFormation(event: any) {
    this.FleetFormation = event;
    this.saveData.saveString('own-data.fleet_formation', this.FleetFormation);
  }

  /**
   * 陣形の種類を表す文字列
   */
  get fleetTypeString(): string{
    const fleetTypeInt = parseInt(this.FleetType);
    if (fleetTypeInt === 0) {
      return '通常';
    }else if(fleetTypeInt === 1){
      return '遊撃';
    }else{
      return '連合';
    }
  }
}
