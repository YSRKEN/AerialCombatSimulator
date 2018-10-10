import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-lbasunit',
  templateUrl: './lbasunit.component.html',
  styleUrls: ['./lbasunit.component.scss']
})
export class LBASUnitComponent implements OnInit {

  /**
   * 装備一覧
   */
  WeaponList: { "value": string, "name": string }[] = [
    {"value":"なし", "name":"なし"},
    {"value":"烈風", "name":"烈風"},
    {"value":"流星", "name":"流星"},
    {"value":"彗星", "name":"彗星"},
  ];

  /**
   * 選択している装備
   */
  SelectedWeapon: string[] = ['','','',''];

  /**
   * 基地航空隊の番号
   */
  @Input() index: string = '1';
  IndexString: string;

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    // 基地航空隊の番号を設定
    const indexToString = {'1': '一', '2': '二', '3': '三'};
    this.IndexString = '第' + indexToString[this.index] + '航空隊';

    /**
     * 設定を読み込む
     */
    const weaponCount = 4;
    for(let i = 0; i < weaponCount; ++i){
      this.SelectedWeapon[i] = this.saveData.loadString('lbasunit.selected_weapon_' + this.index + '' + (i + 1), 'なし');
    }
  }

  /**
   * 装備の選択を切り替えた際の処理
   * @param event 
   */
  changeSelectedWeapon(event: any, index: number){
    this.SelectedWeapon[index] = event;
    this.saveData.saveString('lbasunit.selected_weapon_' + this.index + '' + (index + 1), this.SelectedWeapon[index]);
  }
}
