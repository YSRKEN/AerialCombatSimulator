import { Injectable } from '@angular/core';
import { SaveDataService } from './save-data.service';

@Injectable({
  providedIn: 'root'
})
export class UtilityService {

  constructor(private saveData: SaveDataService) { }

  getLBASData(index: number): {} {
    // 発進数が0であるものは飛ばす
    const count = this.saveData.loadString('lbasunit.[' + index + '].lbas_count', '0');
    if (count  == '0') {
      return {'count': '0'};
    }

    const lbasUnit = {'count': count, 'weapon': []};

    // 各スロットの情報を確認する
    for (let j = 1; j <= 4; ++j) {
      // 装備名を確認し、「なし」なら飛ばす
      const prefix = 'lbasunit.[' + index + '].[' + j + ']';
      const name = this.saveData.loadString(prefix + '.weapon_name', '0');
      if (name == '0') {
        continue;
      }

      // 情報をまとめる
      const lbasWeapon = {
        'id': name,
        'rf': this.saveData.loadString(prefix + '.weapon_rf', '0'),
        'mas': this.saveData.loadString(prefix + '.weapon_mas', '7'),
        'slot_count': this.saveData.loadString(prefix + '.slot_count', '0'),
      };
      lbasUnit.weapon.push(lbasWeapon);
    }
    return lbasUnit;
  }
}
