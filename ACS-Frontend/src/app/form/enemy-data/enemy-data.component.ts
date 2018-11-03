import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { RestApiService } from '../../service/rest-api.service';

@Component({
  selector: 'app-enemy-data',
  templateUrl: './enemy-data.component.html',
  styleUrls: ['./enemy-data.component.scss']
})
export class EnemyDataComponent implements OnInit {
  /**
   * マップ一覧
   */
  MapList: { "value": string, "name": string }[] = [];

  /**
   * マップの難易度一覧
   */
  LevelList: { "value": string, "name": string }[] = [
    {"value":"0", "name":"甲"},
    {"value":"1", "name":"乙"},
    {"value":"2", "name":"丙"},
    {"value":"3", "name":"丁"},
  ];

  /**
   * マップのマス一覧
   */
  PointList: { "value": string, "name": string }[] = [];

  /**
   * マップの画像URL
   */
  MapUrl: string = '';

  /**
   * 編成情報
   */
  FleetInfo: string = '';

  constructor(private saveData: SaveDataService, private restApi: RestApiService) { }

  async ngOnInit() {
    // マップリストを初期化
    this.MapList = (await this.restApi.getMapNames())
    .map(v => {return {'value': '' + v, 'name': v}});

    // マスリストを初期化
    this.PointList = (await this.restApi.getMapPositions(this.SelectedMap))
      .map(v => {return {'value': '' + v, 'name': v}});

    // マップ名を初期化
    this.MapUrl = await this.restApi.getMapUrl(this.SelectedMap);

    // 編成情報を初期化
    this.FleetInfo = await this.restApi.getFleetInfo(this.SelectedMap, this.SelectedPoint, this.SelectedLevel);

    // ダミー値
    /*
    this.FleetInfo = "輪形陣\n";
    this.FleetInfo +=  "(1)北方棲姫 Lv1　[0]5inch単装高射砲,[64]深海猫艦戦,[68]深海地獄艦爆,[40]深海復讐艦攻\n";
    this.FleetInfo += "(2)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦爆 Mark.II\n";
    this.FleetInfo += "(3)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    this.FleetInfo += "(4)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    this.FleetInfo += "(5)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    this.FleetInfo += "(6)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    */
  }

  /**
   * 難易度選択のセレクトボックスを、イベント海域じゃないと表示させない仕掛け
   */
  get DisableLevelSelect(){
    return (this.SelectedMap.length > 0 && this.SelectedMap.substr(0, 1) != "E");
  }

  /**
   * マップの選択
   */
  get SelectedMap(): string {
    return this.saveData.loadString('enemy-data.selected_map', '1-1');
  }
  set SelectedMap(value: string) {
    // 保存
    this.saveData.saveString('enemy-data.selected_map', value);

    // 艦名リストを更新
    this.restApi.getMapPositions(this.SelectedMap)
    .then(value => {
        this.PointList = value.map(v => {return {'value': '' + v, 'name': v}});
    });

    // マップ名を更新
    this.restApi.getMapUrl(this.SelectedMap)
    .then(value => {
        this.MapUrl = value;
    });
  }

  /**
   * マップの難易度選択
   */
  get SelectedLevel(): string {
    return this.saveData.loadString('enemy-data.selected_level', '0');
  }
  set SelectedLevel(value: string) {
    this.saveData.saveString('enemy-data.selected_level', value);
  }

  /**
   * マップのマス選択
   */
  get SelectedPoint(): string {
    return this.saveData.loadString('enemy-data.selected_point', 'A-1');
  }
  set SelectedPoint(value: string) {
    // 保存
    this.saveData.saveString('enemy-data.selected_point', value);

    // 敵編成表示を更新
    this.restApi.getFleetInfo(this.SelectedMap, this.SelectedPoint, this.SelectedLevel)
    .then(value => {
        this.FleetInfo = value;
    });
  }
}
