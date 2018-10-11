import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-own-unit',
  templateUrl: './own-unit.component.html',
  styleUrls: ['./own-unit.component.scss']
})
export class OwnUnitComponent implements OnInit {

  /**
   * 艦隊の番号
   */
  @Input() index: string = '1';

  /**
   * 艦隊の種類
   */
  @Input() type: string = '0';

  constructor() { }

  ngOnInit() {
  }

  get UnitString(): string {
    if (parseInt(this.type) < 2){
      return this.index + '番艦';
    } else {
      const indexInt = parseInt(this.index) - 1;
      return '第' + (Math.floor(indexInt / 6) + 1) + '艦隊 ' + ((indexInt % 6) + 1).toString() + '番艦';
    }
  }
}
