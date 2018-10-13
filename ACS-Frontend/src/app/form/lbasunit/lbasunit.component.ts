import { Component, OnInit, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';

@Component({
  selector: 'app-lbasunit',
  templateUrl: './lbasunit.component.html',
  styleUrls: ['./lbasunit.component.scss']
})
export class LBASUnitComponent implements OnInit {
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
  }

  /**
   * 基地航空隊の状態
   */
  get LBASCountValue(): string {
    return this.saveData.loadString('lbasunit.[' + this.index + '].lbas_count', '0');
  }
  set LBASCountValue(value: string) {
    this.saveData.saveString('lbasunit.[' + this.index + '].lbas_count', value);
  }
}
