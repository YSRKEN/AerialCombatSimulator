import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { UtilityService } from 'src/app/service/utility.service';
import { RestApiService } from 'src/app/service/rest-api.service';

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
        {"value":"3", "name":"梯形陣"},
        {"value":"4", "name":"単横陣"},
        {"value":"5", "name":"警戒陣"},
      ];
    }else{
      return [
        {"value":"14", "name":"第一警戒航行序列(対潜警戒)"},
        {"value":"11", "name":"第二警戒航行序列(前方警戒)"},
        {"value":"12", "name":"第三警戒航行序列(輪形陣)"},
        {"value":"10", "name":"第四警戒航行序列(戦闘隊形)"},
      ];
    }
  }

  /**
   * 艦隊の陣形一覧
   */
  FleetFormationList: { "value": string, "name": string }[];

  /**
   * 制空値(特殊)
   */
  AntiAirValue1: string = '0';

  /**
   * 制空値(通常)
   */
  AntiAirValue2: string = '0';

  /**
   * 制空判定(特殊)
   */
  Status1: string = '';

  /**
   * 制空判定(通常)
   */
  Status2: string = '';

  /**
   * 艦隊防空値
   */
  AntiAirBonus: string = '';

  /**
   * 加重対空値
   */
  WeightedAntiAir: number[] = [];

  constructor(private saveData: SaveDataService,
    private utility: UtilityService,
    private restApi: RestApiService) { }

  ngOnInit() {
    this.FleetFormationList = this.getFleetFormationList(this.fleetTypeString);

    // 制空値を計算する
    this.calcAAV();
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

  /**
   * 制空値を計算し直す
   */
  async calcAAV() {
    const ownUnit = this.utility.getOwnData();
  
    // サーバーにクエリを投げる
    const ownInfo = await this.restApi.postOwnInfo(ownUnit);
    this.AntiAirValue1 = '' + ownInfo['aav1'];
    this.AntiAirValue2 = '' + ownInfo['aav2'];
    this.Status1 = this.utility.calcStatus(ownInfo['aav1'], this.saveData.loadInt('aav1', 0));
    this.Status2 = this.utility.calcStatus(ownInfo['aav2'], this.saveData.loadInt('aav2', 0));
    this.AntiAirBonus = '' + Math.round(ownInfo['aab'] * 10) / 10;
    this.WeightedAntiAir = ownInfo['waa'];
  }
}
