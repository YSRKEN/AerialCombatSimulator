import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-weapon-selector',
  templateUrl: './weapon-selector.component.html',
  styleUrls: ['./weapon-selector.component.scss']
})
export class WeaponSelectorComponent implements OnInit {

  /**
   * 装備種カテゴリ
   * 'LBAS' => 基地航空隊の装備だけ表示する
   * 'Normal' => 全ての装備を表示する
   * その他 => どの装備も表示しない
   */
  @Input() category: string;

  /**
   * 保存時のキーに付ける接頭辞
   */
  @Input() prefix: string;

  /**
   * 装備種リスト
   */
  WeaponTypeList: { "value": string, "name": string }[];

  /**
   * 装備種に適合した装備種リストを返す
   * @param category 装備種カテゴリ
   */
  private getWeaponTypeList(category: string): { "value": string, "name": string }[] {
    switch(category){
      case 'LBAS':
        return [
          { "value": "0", "name": "なし" },
          { "value": "5", "name": "艦戦" },
          { "value": "6", "name": "艦爆" },
          { "value": "7", "name": "艦攻" },
          { "value": "8", "name": "艦偵" },
        ];
      case 'Normal':
        return [
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
      default:
        return [
          { "value": "0", "name": "なし" },
        ];
      }
  }

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    // @Inputをチェックする
    if (this.prefix === undefined || undefined === '') {
      throw new Error("<app-weapon-selector>のprefix属性は省略できません。");
    }

    // 装備種リストを初期化
    this.WeaponTypeList = this.getWeaponTypeList(this.category);
  }

  /**
   * 装備種
   */
  get WeaponType(): string {
    return this.saveData.loadString(this.prefix + '.weapon_type', '0');
  }
  set WeaponType(value: string) {
    this.saveData.saveString(this.prefix + '.weapon_type', value);
  }
}
