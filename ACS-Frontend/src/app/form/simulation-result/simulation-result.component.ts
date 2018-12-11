import { Component, OnInit } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-simulation-result',
  templateUrl: './simulation-result.component.html',
  styleUrls: ['./simulation-result.component.scss']
})
export class SimulationResultComponent implements OnInit {

  SimulationType: string = '1';

  constructor(private saveData: SaveDataService) { }

  ngOnInit() {
    this.SimulationType = this.saveData.loadString('simulation-result.simulation_type', '1');
  }

  /**
   * シミュレーションの種類を切り替えた際の処理
   * @param event 
   */
  changeSimulationType(event: any) {
    this.SimulationType = event;
    this.saveData.saveString('simulation-result.simulation_type', this.SimulationType);
  }

  getEnemyData(): { "map": string, "point": string, "level": string } {
    return {
      "map": this.saveData.loadString('enemy-data.selected_map', '1-1'),
      "point": this.saveData.loadString('enemy-data.selected_point', 'A-1'),
      "level": this.saveData.loadString('enemy-data.selected_level', '0')
    }
  }

  /**
   * シミュレーションを開始する
   */
  startSimulation(){
    console.log(this.getEnemyData());
  }
}
