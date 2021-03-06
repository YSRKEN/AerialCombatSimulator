import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../service/save-data.service';
import { RestApiService } from '../service/rest-api.service';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.scss']
})
export class MainComponent implements OnInit {

  /**
   * 選択モード
   */
  Mode: number;

  constructor(private saveData: SaveDataService, private restApi: RestApiService) { }

  ngOnInit() {
    /**
     * 設定を読み込む
     */
    this.Mode = this.saveData.loadInt('main.mode', 0);
  }

  /**
   * 基地航空隊(Land Base Aerial Support)モードにする
   */
  selectLBASMode(){
    this.Mode = 0;
    this.saveData.saveNumber('main.mode', this.Mode);
  }

  /**
   * 敵艦隊(Enemy Fleet)モードにする
   */
  selectEnemyMode(){
    this.Mode = 1;
    this.saveData.saveNumber('main.mode', this.Mode);
  }

  /**
   * 自艦隊(Own Fleet)モードにする
   */
  selectOwnMode(){
    this.Mode = 2;
    this.saveData.saveNumber('main.mode', this.Mode);
  }

  /**
   * シミュレーション(Simulation)モードにする
   */
  selectSimulationMode(){
    this.Mode = 3;
    this.saveData.saveNumber('main.mode', this.Mode);
  }

  /**
   * LocalStorageに保存したキャッシュを削除する
   */
  clearCache(){
    this.restApi.clearCache();
  }
}
