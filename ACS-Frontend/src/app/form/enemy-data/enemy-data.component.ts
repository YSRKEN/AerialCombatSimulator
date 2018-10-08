import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-enemy-data',
  templateUrl: './enemy-data.component.html',
  styleUrls: ['./enemy-data.component.scss']
})
export class EnemyDataComponent implements OnInit {

  MapUrl: string = "https://vignette.wikia.nocookie.net/kancolle/images/b/b7/3-5_Map.png/revision/latest/scale-to-width-down/700?cb=20180818165502";

  constructor() { }

  ngOnInit() {
  }

}
