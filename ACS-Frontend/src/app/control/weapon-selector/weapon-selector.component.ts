import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-weapon-selector',
  templateUrl: './weapon-selector.component.html',
  styleUrls: ['./weapon-selector.component.scss']
})
export class WeaponSelectorComponent implements OnInit {

  /**
   * 基地航空隊の装備だけ表示するならtrue
   */
  @Input() category: string;

  WeaponTypeList: { "value": string, "name": string }[];

  constructor() { }

  ngOnInit() {
    // 装備種リストを初期化
    switch(this.category){
    case 'LBAS':
      this.WeaponTypeList = [
        { "value": "0", "name": "なし" },
        { "value": "5", "name": "艦戦" },
        { "value": "6", "name": "艦爆" },
        { "value": "7", "name": "艦攻" },
        { "value": "8", "name": "艦偵" },
      ];
      break;
    case 'Normal':
      this.WeaponTypeList = [
        { "value": "0", "name": "なし" },
        { "value": "1", "name": "主砲" },
        { "value": "2", "name": "副砲" },
        { "value": "3", "name": "魚雷" },
        { "value": "5", "name": "艦戦" },
        { "value": "6", "name": "艦爆" },
        { "value": "7", "name": "艦攻" },
        { "value": "8", "name": "艦偵" },
        { "value": "11", "name": "水偵" },
      ];
      break;
    default:
      this.WeaponTypeList = [
        { "value": "0", "name": "なし" },
      ];
      break;
    }
  }
}
