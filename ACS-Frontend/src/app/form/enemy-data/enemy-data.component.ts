import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-enemy-data',
  templateUrl: './enemy-data.component.html',
  styleUrls: ['./enemy-data.component.scss']
})
export class EnemyDataComponent implements OnInit {
  /**
   * マップ一覧
   */
  MapList: { "value": string, "name": string }[] = [
    {"value":"1-1", "name":"1-1"},
    {"value":"3-5", "name":"3-5"},
    {"value":"E-4", "name":"E-4"},
  ];

  /**
   * マップの選択
   */
  SelectedMap: string;

  /**
   * マップの難易度一覧
   */
  LevelList: { "value": string, "name": string }[] = [
    {"value":"甲", "name":"甲"},
    {"value":"乙", "name":"乙"},
    {"value":"丙", "name":"丙"},
    {"value":"丁", "name":"丁"},
  ];

  /**
   * マップの難易度選択
   */
  SelectedLevel: string = "甲";

  /**
   * マップのマス一覧
   */
  PointList: { "value": string, "name": string }[] = [
    {"value":"B-1", "name":"B-1"},
    {"value":"D-2", "name":"D-2"},
    {"value":"H-6 (Last)", "name":"H-6 (Last)"},
    {"value":"K-3", "name":"K-3"},
  ];

  /**
   * マップの難易度選択
   */
  SelectedPoint: string = "H-6 (Last)";

  /**
   * マップ画像
   */
  MapUrl: string = "https://vignette.wikia.nocookie.net/kancolle/images/b/b7/3-5_Map.png/revision/latest/scale-to-width-down/700?cb=20180818165502";

  FleetInfo: string;

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    // ダミー値
    this.FleetInfo = "輪形陣\n";
    this.FleetInfo +=  "(1)北方棲姫 Lv1　[0]5inch単装高射砲,[64]深海猫艦戦,[68]深海地獄艦爆,[40]深海復讐艦攻\n";
    this.FleetInfo += "(2)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦爆 Mark.II\n";
    this.FleetInfo += "(3)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    this.FleetInfo += "(4)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    this.FleetInfo += "(5)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";
    this.FleetInfo += "(6)護衛要塞 Lv1　[0]8inch三連装砲,[35]深海棲艦戦 Mark.II,[35]深海棲艦攻 Mark.II\n";

    /**
     * 設定を読み込む
     */
    this.SelectedMap = this.saveData.loadString('enemy-data.selected_map', '3-5');
    this.SelectedLevel = this.saveData.loadString('enemy-data.selected_level', '甲');
    this.SelectedPoint = this.saveData.loadString('enemy-data.selected_point', 'H-6 (Last)');
  }

  /**
   * 難易度選択のセレクトボックスを、イベント海域じゃないと表示させない仕掛け
   */
  get DisableLevelSelect(){
    return (this.SelectedMap.length > 0 && this.SelectedMap.substr(0, 1) != "E");
  }

  /**
   * マップの選択を切り替えた際の処理
   * @param event 
   */
  changeSelectedMap(event: any){
    this.SelectedMap = event;
    this.saveData.saveString('enemy-data.selected_map', this.SelectedMap);
  }

  /**
   * 難易度の選択を切り替えた際の処理
   * @param event 
   */
  changeSelectedLevel(event: any){
    this.SelectedLevel = event;
    this.saveData.saveString('enemy-data.selected_level', this.SelectedLevel);
  }

  /**
   * マスの選択を切り替えた際の処理
   * @param event 
   */
  changeSelectedPoint(event: any){
    this.SelectedPoint = event;
    this.saveData.saveString('enemy-data.selected_point', this.SelectedPoint);
  }
}
