import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { UtilityService } from 'src/app/service/utility.service';
import { RestApiService } from 'src/app/service/rest-api.service';

@Component({
  selector: 'app-lbasunit',
  templateUrl: './lbasunit.component.html',
  styleUrls: ['./lbasunit.component.scss']
})
export class LBASUnitComponent implements OnInit {
  /**
   * 基地航空隊の番号
   */
  @Input() index: string = '1';
  IndexString: string;

  /**
   * 戦闘行動半径
   */
  Radius: string;

  /**
   * 制空値
   */
  AntiAirValue: string;

  /**
   * 制空判定
   */
  Status: string;

  constructor(
    private saveData: SaveDataService,
    private utility: UtilityService,
    private restApi: RestApiService
    ) { }

  ngOnInit() {
    // 基地航空隊の番号を設定
    const indexToString = {'1': '一', '2': '二', '3': '三'};
    this.IndexString = '第' + indexToString[this.index] + '航空隊';

    // 戦闘行動半径と制空値を計算する
    this.calcRadiusAAV();
  }

  /**
   * 基地航空隊の状態
   */
  get LBASCountValue(): string {
    return this.saveData.loadString('lbasunit.[' + this.index + '].lbas_count', '0');
  }
  set LBASCountValue(value: string) {
    this.saveData.saveString('lbasunit.[' + this.index + '].lbas_count', value);
  }

  /**
   * 制空値・戦闘行動半径を計算し直す
   */
  async calcRadiusAAV() {
    if (parseInt(this.LBASCountValue) == 0) {
      this.Radius = '0';
      this.AntiAirValue = '0';
    } else {
      const lbasUnit = this.utility.getLBASData(parseInt(this.index));
  
      // サーバーにクエリを投げる
      const lbasInfo = await this.restApi.postLbasInfo(lbasUnit);
      this.Radius = '' + lbasInfo['Radius'];
      this.AntiAirValue = '' + lbasInfo['AntiAirValue'];
      this.Status = this.utility.calcStatus(lbasInfo['AntiAirValue'], this.saveData.loadInt('aav1', 0));
    }
  }
}
