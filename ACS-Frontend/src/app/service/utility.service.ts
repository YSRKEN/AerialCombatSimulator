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

    /**
   * 自艦隊のデータを取得する
   */
  getOwnData(): {} {
    const data: {} = {};
    data['formation'] = this.saveData.loadString('own-data.fleet_type', '0');
    data['fleet'] = [];
    for (let fi = 1; fi <= 12; ++fi) {
      // 艦娘が選択されていないものは飛ばす
      const fleetName = this.saveData.loadString('own-unit.[' + fi + '].kammusu_name', '0');
      if (fleetName == '0') {
        continue;
      }

      const fleetData = {'name': fleetName, 'weapon': []};

      // 各スロットの情報を確認する
      for (let wi = 1; wi <= 5; ++wi) {
        // 装備名を確認し、「なし」なら飛ばす
        const prefix = 'own-unit.[' + fi + '].[' + wi + ']';
        const name = this.saveData.loadString(prefix + '.weapon_name', '0');
        if (name == '0') {
          continue;
        }

        // 情報をまとめる
        const fleetWeapon = {
          'id': name,
          'rf': this.saveData.loadString(prefix + '.weapon_rf', '0'),
          'mas': this.saveData.loadString(prefix + '.weapon_mas', '7'),
          'slot_count': this.saveData.loadString(prefix + '.slot_count', '0'),
        };
        fleetData.weapon.push(fleetWeapon);
      }
      data['fleet'].push(fleetData);
    }
    return data;
  }

  calcStatus(friendAAV: number, enemyAAV: number): string {
    if (friendAAV >= enemyAAV * 3) {
      return "確保";
    } else if (friendAAV * 2 >= enemyAAV * 3) {
      return "優勢";
    } else if (friendAAV * 3 > enemyAAV * 2) {
      return "均衡";
    } else if (friendAAV * 3 > enemyAAV) {
      return "劣勢";
    } else {
      return "喪失";
    }
  }
}
