import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-own-data',
  templateUrl: './own-data.component.html',
  styleUrls: ['./own-data.component.scss']
})
export class OwnDataComponent implements OnInit {

  FleetType: string;

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    this.FleetType = this.saveData.loadString('own-data.fleet_type', '0');
  }

  /**
   * 搭載数の選択を切り替えた際の処理
   * @param event 
   */
  changeFleetType(event: any){
    this.FleetType = event;
    this.saveData.saveString('own-data.fleet_type', this.FleetType);
  }

  get fleetTypeString(): string{
    const fleetTypeInt = parseInt(this.FleetType);
    if (fleetTypeInt === 0) {
      return '通常';
    }else if(fleetTypeInt === 1){
      return '遊撃';
    }else{
      return '連合';
    }
  }
}
