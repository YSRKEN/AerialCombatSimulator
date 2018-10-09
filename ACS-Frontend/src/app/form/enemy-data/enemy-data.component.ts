import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-enemy-data',
  templateUrl: './enemy-data.component.html',
  styleUrls: ['./enemy-data.component.scss']
})
export class EnemyDataComponent implements OnInit {

  /**
   * 現在選択しているマップ
   */
  SelectedMap: string = '3-5';

  /**
   * マップ一覧
   */
  MapList: string[] = ["1-1","3-5","E-3"];

  /**
   * マップの難易度一覧
   */
  LevelList: string[] = ["甲", "乙", "丙", "丁"];

  /**
   * マップ画像
   */
  MapUrl: string = "https://vignette.wikia.nocookie.net/kancolle/images/b/b7/3-5_Map.png/revision/latest/scale-to-width-down/700?cb=20180818165502";

  constructor() { }

  ngOnInit() {
  }

  get DisableLevelSelect(){
    return (this.SelectedMap.length > 0 && this.SelectedMap.substr(0, 1) == "E");
  }

  hoge(){
    console.log("test");
  }
}
