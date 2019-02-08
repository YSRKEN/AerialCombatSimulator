import { Component, OnInit, ViewChild, ElementRef, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { RestApiService } from 'src/app/service/rest-api.service';
import { Chart, ChartData, ChartOptions } from 'chart.js'
import { pairs } from 'rxjs';

@Component({
  selector: 'app-simulation-result',
  templateUrl: './simulation-result.component.html',
  styleUrls: ['./simulation-result.component.scss']
})
export class SimulationResultComponent implements OnInit {

  @ViewChild('canvas')
  ref: ElementRef;
  data: ChartData;
  context: CanvasRenderingContext2D;
  chart: Chart;

  SimulationType: string = '1';

  constructor(
    private saveData: SaveDataService,
    private restApi: RestApiService,
    private _elementRef: ElementRef) { }

  ngOnInit() {
    this.SimulationType = this.saveData.loadString('simulation-result.simulation_type', '1');

    this.data = {
      datasets: [{
        label: '確率分布',
        type: "line",
        showLine: true,
        lineTension: 0,
        borderColor: "rgba(160,194,56,1)",
        backgroundColor: "rgba(160,194,56,0.4)",
        pointBorderColor: "rgba(160,194,56,1)",
        data: [],
        yAxisID: 'y-right'
      },{
        label: '下側確率',
        type: "line",
        showLine: true,
        lineTension: 0,
        borderColor: "rgba(242,207,1,1)",
        backgroundColor: "rgba(242,207,1,0.4)",
        pointBorderColor: "rgba(242,207,1,1)",
        data: [],
      }]
    };
  }

  ngAfterViewInit() {
    // canvasを取得
    this.context = this.ref.nativeElement.getContext('2d');

    // チャートの作成
    this.chart = new Chart(this.context, {
      type: 'scatter',
      data: this.data,
      options: {
        scales: {
          xAxes: [{
            display: true,
            scaleLabel: { display: true, labelString: '制空値' },
            ticks: { stepSize: 1 }
          }],
          yAxes: [{
            display: true,
            scaleLabel: { display: true, labelString: '下側確率の割合(％)' },
            ticks: { min: 0, max: 100, stepSize: 10 }
          },
          {
            display: true,
            scaleLabel: { display: true, labelString: '確率分布の割合(％)' },
            ticks: { min: 0 },
            id: 'y-right',
            position: 'right'
          }]
        }
      }
    })
    this.data.datasets[0].data = [{x: 10, y: 30},{x: 11, y: 40},{x: 12, y: 30},]
    this.data.datasets[1].data = [{x: 10, y: 30},{x: 11, y: 70},{x: 12, y: 100},]
    this.chart.update();
  }

  /**
   * シミュレーションの種類を切り替えた際の処理
   * @param event 
   */
  changeSimulationType(event: any) {
    this.SimulationType = event;
    this.saveData.saveString('simulation-result.simulation_type', this.SimulationType);
  }

  /**
   * 基地航空隊のデータを取得する
   */
  getLBASData(): {}[] {
    const data: {}[] = [];
    for (let i = 1; i <= 3; ++i) {
      // 発進数が0であるものは飛ばす
      const count = this.saveData.loadString('lbasunit.[' + i + '].lbas_count', '0');
      if (count  == '0') {
        continue;
      }

      const lbasUnit = {'count': count, 'weapon': []};

      // 各スロットの情報を確認する
      for (let j = 1; j <= 4; ++j) {
        // 装備名を確認し、「なし」なら飛ばす
        const prefix = 'lbasunit.[' + i + '].[' + j + ']';
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

      data.push(lbasUnit);
    }
    return data;
  }

  /**
   * 敵艦隊の情報を取得する
   */
  getEnemyData(): { "map": string, "point": string, "level": string } {
    return {
      "map": this.saveData.loadString('enemy-data.selected_map', '1-1'),
      "point": this.saveData.loadString('enemy-data.selected_point', 'A-1'),
      "level": this.saveData.loadString('enemy-data.selected_level', '0')
    }
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

  /**
   * シミュレーションを開始する
   */
  async startSimulation(){
    // 情報を取得する
    const lbas = this.getLBASData();
    const enemy = this.getEnemyData();
    const own = this.getOwnData();

    // サーバーにクエリを投げる
    const simulationResult = await this.restApi.postSimulation(lbas, enemy, own, this.SimulationType);

    // サーバーから返ってきた結果を処理する
    console.log(simulationResult);
    const enemyAntiAirValueDict: { [key: number]: number; } = simulationResult['EnemyAntiAirValue'];
    this.redrawEnemyAntiAirValue(enemyAntiAirValueDict);
  }

  /**
   * 敵制空値の連想配列から、グラフ描画用のデータに変換する
   * @param enemyAntiAirValueDict 敵制空値の連想配列。dict[制空値]=出現回数
   */
  redrawEnemyAntiAirValue( enemyAntiAirValueDict: { [key: number]: number; }) {
    // 反復回数の合計値を出す
    var sum = 0;
    for (var aav in enemyAntiAirValueDict) {
      var count = enemyAntiAirValueDict[aav];
      sum += count;
    }

    // 割合の表と累積の表を両方作成する
    var graph1: {x: number, y: number}[] = [];
    var graph2: {x: number, y: number}[] = [];
    var sum2 = 0;
    for (let aav in enemyAntiAirValueDict) {
      var count = enemyAntiAirValueDict[aav];
      graph1.push({x: parseInt(aav), y: 100.0 * count / sum});
      sum2 += count;
      graph2.push({x: parseInt(aav), y: 100.0 * sum2 / sum});
    }

    // 累積割合がX％を超えた点を検索する
    var thresholdProbList = [50.0, 70.0, 90.0, 95.0, 99.0];
    var titleText = '計算結果(';
    for (let i = 0; i < thresholdProbList.length; ++i) {
      if (i > 0) {
        titleText += "　";
      }
      let prob = thresholdProbList[i];
      titleText += '' + prob + '％：' + graph2.find(pair => pair.y >= prob).x;
    }
    titleText += ')';

    // グラフに計算結果をセットする
    console.log(graph1)
    console.log(graph2)
    this.data.datasets[0].data = graph1
    this.data.datasets[1].data = graph2
    this.chart.config.options.title.display = true;
    this.chart.config.options.title.text = titleText;
    this.chart.update()
  }
}
