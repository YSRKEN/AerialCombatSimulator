import { Component, OnInit } from '@angular/core';

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
   * マップの難易度選択
   */
  SelectedMap: string = "3-5";

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
   * マップ画像
   */
  MapUrl: string = "https://vignette.wikia.nocookie.net/kancolle/images/b/b7/3-5_Map.png/revision/latest/scale-to-width-down/700?cb=20180818165502";

  constructor() { }

  ngOnInit() {
  }

  get DisableLevelSelect(){
    return (this.SelectedMap.length > 0 && this.SelectedMap.substr(0, 1) != "E");
  }

  hoge(){
    console.log("test");
  }
}
