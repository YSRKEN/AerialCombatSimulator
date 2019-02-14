import { Component, OnInit, ViewChild, ElementRef, Input } from '@angular/core';
import { SaveDataService } from '../../service/save-data.service';
import { RestApiService } from 'src/app/service/rest-api.service';
import { Chart, ChartData, ChartOptions } from 'chart.js'
import { pairs } from 'rxjs';
import { UtilityService } from 'src/app/service/utility.service';

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

  @ViewChild('canvas2')
  ref2: ElementRef;
  context2: CanvasRenderingContext2D;
  chart2: Chart;

  SimulationType: string = '1';

  simulationFlg: boolean = false;

  constructor(
    private saveData: SaveDataService,
    private restApi: RestApiService,
    private utility: UtilityService,
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

    this.context2 = this.ref2.nativeElement.getContext('2d');

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

    this.chart2 = new Chart(this.context2, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [],
      },
      options: {
        title: {
          display: true,
          text: '制空状況',
        },
        scales: {
          xAxes: [{
            stacked: true,
            categoryPercentage:0.4,
            scaleLabel: { display: true, labelString: '基地航空隊/自艦隊' },
          }],
          yAxes: [{
            stacked: true,
            scaleLabel: { display: true, labelString: '制空状況の割合(％)' },
          }]
        },
        legend: {
          labels: {
            boxWidth:30,
            padding:20
          },
          display: true
        },
        tooltips:{
          mode:'label'
        }
      }
    })
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
      const temp = this.utility.getLBASData(i);
      if (parseInt(temp['count']) > 0) {
        data.push(temp);
      }
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
   * シミュレーションを開始する
   */
  async startSimulation(){
    if (this.simulationFlg) {
      return;
    }
    this.simulationFlg = true;

    // 情報を取得する
    const lbas = this.getLBASData();
    const enemy = this.getEnemyData();
    const own = this.utility.getOwnData();

    // サーバーにクエリを投げる
    const simulationResult = await this.restApi.postSimulation(lbas, enemy, own, this.SimulationType);

    // サーバーから返ってきた結果を処理する
    const enemyAntiAirValueDict: { [key: number]: number; } = simulationResult['EnemyAntiAirValue'];
    this.redrawEnemyAntiAirValue(enemyAntiAirValueDict);
    const antiAirStatusList: number[][] = simulationResult['LbasStatus'];
    this.redrawAntiAirStatus(antiAirStatusList);

    this.simulationFlg = false;
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
    this.data.datasets[0].data = graph1;
    this.data.datasets[1].data = graph2;
    this.chart.config.options.title.display = true;
    this.chart.config.options.title.text = titleText;
    this.chart.update();
  }

  /**
   * 制空状況の配列から、グラフ描画用のデータに変換する
   * @param antiAirStatusList 制空状況の配列
   */
  redrawAntiAirStatus(antiAirStatusList: number[][]) {
    // 出撃させた基地航空隊の名称一覧を作る
    const labelList: string[] = [];
    if (this.SimulationType != '2') {
      for (let i = 1; i <= 3; ++i) {
        // 発進数が0であるものは飛ばす
        const count = this.saveData.loadString('lbasunit.[' + i + '].lbas_count', '0');
        if (count  == '0') {
          continue;
        }
  
        // 一覧に追加する
        for(let j = 1; j <= parseInt(count); ++j) {
          labelList.push('' + i + '-' + j);
        }
      }
    }
    if (this.SimulationType != '1') {
      labelList.push('本隊');
    }

    // グラフを描画する
    this.chart2.data.labels = labelList;
    this.chart2.data.datasets = [];
    const statusNameList = ['確保', '優勢', '均衡', '劣勢', '喪失'];
    const statusColorList = ['#4E9A06', '#C88D00', '#CC0000', '#204A87', '#FF0000'];
    const loopCount = 10000;
    for (let i = statusNameList.length - 1; i >= 0; --i) {
      const temp = {
        label: statusNameList[i],
        borderWith: 1,
        backgroundColor: statusColorList[i],
        borderColor: statusColorList[i],
        data: antiAirStatusList.map(list => Math.round(1000.0 * list[i] / loopCount) / 10)
      };
      this.chart2.data.datasets.push(temp);
    }
    this.chart2.update();
  }
}
