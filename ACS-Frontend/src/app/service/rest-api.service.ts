import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SaveDataService } from './save-data.service';

@Injectable({
  providedIn: 'root'
})
export class RestApiService {

  /**
   * アクセスする先のサーバーアドレス
   */
  private serverUrl = "http://localhost:8080";

  /**
   * セマフォ
   */
  private semaphore: boolean = false;

  /**
   * コンストラクタ
   * @param http HTTPクライアント
   */
  constructor(private http: HttpClient, private saveData: SaveDataService) {
    // ローカルサーバーで動いていない際は、本番用serverにアクセスするようにする
    if (window.location.href.indexOf("localhost") < 0){
      this.serverUrl = "https://aerial-combat-service.appspot.com";
    }
  }

  /**
   * データキャッシュ
   */
  private getCache<T>(key: string): T | null {
    const cacheData = this.saveData.loadObject<{[key: string]: any; }>('rest-api.cache', {});
    if (key in cacheData) {
      return <T>(cacheData[key]);
    } else {
      return null;
    }
  }
  private setCache<T>(key: string, value: T) {
    const cacheData = this.saveData.loadObject<{[key: string]: any; }>('rest-api.cache', {});
    cacheData[key] = value;
    this.saveData.saveObject('rest-api.cache', cacheData);
  }
  clearCache() {
    this.saveData.saveObject('rest-api.cache', {});
  }

  /**
   * キャッシュ機能を含んだGETクライアント
   * @param key キャッシュのキー
   * @param endpoint エンドポイントURL
   */
  private async getRequest<T>(key: string, endpoint: string): Promise<T | null> {
    try {
      // キャッシュに存在する場合はそちらを返却する
      const cache = this.getCache<T>(key);
      if (cache != null) {
        console.log("[cache] " + key);
        return cache;
      }

      // セマフォが立っている際は、何かしらの通信中なので、読み込みを待機する
      if (this.semaphore) {
        await new Promise(resolve => setTimeout(resolve, 1));
        return this.getRequest<T>(key, endpoint);
      }

      // 寝ているセマフォを立て、通信後にまた寝かせる
      console.log("[non-cache] " + key);
      this.semaphore = true;
      const result = await this.http.get<T>(this.serverUrl + '/' + endpoint).toPromise();
      this.setCache<T>(key, result);
      this.semaphore = false;

      return result;
    } catch (e) {
      console.log(e);
      return null;
    }
  }

  /**
   * weapon-typesエンドポイント
   * @param category カテゴリ。「LBAS」か「Normal」を指定する
   * @param short_name_flg 装備種の名前を短くするならtrue、しないならfalse
   */
  public async getWeaponTypes(category: string = '', short_name_flg: boolean = false): Promise<{"id": string, "name": string}[]> {
    // 準備をする
    const key = 'getWeaponTypes#' + category + ',' + (short_name_flg ? 1 : 0);
    const endpoint = 'weapon-types?category=' + category + '&short_name_flg=' + (short_name_flg ? 1 : 0);

    // 結果を取得する
    const result = await this.getRequest<{"id": string, "name": string}[]>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }

  /**
   * weapon-namesエンドポイント
   * @param type 装備種のID。0なら未指定
   */
  public async getWeaponNames(type: number = 0, for_kammusu_flg: boolean = true): Promise<{"id": string, "name": string}[]> {
    // 準備をする
    const key = 'getWeaponNames#' + type + ',' + (for_kammusu_flg ? 1 : 0);
    const endpoint = 'weapon-names?type=' + type + '&for_kammusu_flg=' + (for_kammusu_flg ? 1 : 0);

    // 結果を取得する
    const result = await this.getRequest<{"id": string, "name": string}[]>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }

  /**
   * kammusu-typesエンドポイント
   * @param category カテゴリ。「LBAS」か「Normal」を指定する
   * @param short_name_flg 装備種の名前を短くするならtrue、しないならfalse
   */
  public async getKammusuTypes(short_name_flg: boolean = false): Promise<{"id": string, "name": string}[]> {
    // 準備をする
    const key = 'getKammusuTypes#' + (short_name_flg ? 1 : 0);
    const endpoint = 'kammusu-types?short_name_flg=' + (short_name_flg ? 1 : 0);

    // 結果を取得する
    const result = await this.getRequest<{"id": string, "name": string}[]>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }

  /**
   * kammusu-namesエンドポイント
   * @param type 装備種のID。0なら未指定
   */
  public async getKammusuNames(type: number = 0, kammusu_flg: boolean = true): Promise<{"id": string, "name": string, 'slot': number[]}[]> {
    // 準備をする
    const key = 'getKammusuNames#' + type + ',' + (kammusu_flg ? 1 : 0);
    const endpoint = 'kammusu-names?type=' + type + '&kammusu_flg=' + (kammusu_flg ? 1 : 0);

    // 結果を取得する
    const result = await this.getRequest<{"id": string, "name": string, 'slot': number[]}[]>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }

  /**
   * map-namesエンドポイント
   */
  public async getMapNames(): Promise<string[]> {
    // 準備をする
    const key = 'getMapNames';
    const endpoint = 'map-names';

    // 結果を取得する
    const result = await this.getRequest<string[]>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }

  /**
   * map-positionsエンドポイント
   * @param map マップ名
   */
  public async getMapPositions(map: string): Promise<string[]> {
    // 準備をする
    const key = 'getMapPositions#' + map;
    const endpoint = 'map-positions?map=' + map;

    // 結果を取得する
    const result = await this.getRequest<string[]>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }

  /**
   * map-urlエンドポイント
   * @param map マップ名
   */
  public async getMapUrl(map: string): Promise<string> {
    // 準備をする
    const key = 'getMapUrl#' + map;
    const endpoint = 'map-url?map=' + map;

    // 結果を取得する
    const result = await this.getRequest<string>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return '';
    }

    // 成功時の処理
    return result;
  }

  /**
   * fleet-infoエンドポイント
   * @param map マップ名
   */
  public async getFleetInfo(map: string, point: string, level: string): Promise<{}> {
    // 準備をする
    const key = 'getFleetInfo#' + map + ',' + point + ',' + level;
    const endpoint = 'fleet-info?map=' + map + '&point=' + point + '&level=' + level;

    // 結果を取得する
    const result = await this.getRequest<{}>(key, endpoint);

    // 失敗時の処理
    if (result === null) {
      return {};
    }

    // 成功時の処理
    return result;
  }

  /**
   * /simulationエンドポイント
   * @param lbas 基地航空隊
   * @param enemy 敵艦隊
   * @param own 自艦隊
   * @param type シミュレーションの種類
   */
  public async postSimulation(lbas: {}[], enemy: {}, own: {}, type: string): Promise<{}> {
    try {
      // セマフォが立っている際は、何かしらの通信中なので、読み込みを待機する
      if (this.semaphore) {
        await new Promise(resolve => setTimeout(resolve, 1));
        return this.postSimulation(lbas, enemy, own, type);
      }

      // 寝ているセマフォを立て、通信後にまた寝かせる
      this.semaphore = true;
      const endpoint = 'simulation?type=' + type;
      const result = await this.http.post<{}>(this.serverUrl + '/' + endpoint,
        JSON.stringify({
          'lbas': lbas,
          'enemy': enemy,
          'own': own
        })
      ).toPromise();
      this.semaphore = false;

      return result;
    } catch (e) {
      console.log(e);
      return {};
    }
  }

  /**
   * /lbas-infoエンドポイント
   * @param lbas 基地航空隊
   */
  public async postLbasInfo(lbas: {}): Promise<{}> {
    try {
      // セマフォが立っている際は、何かしらの通信中なので、読み込みを待機する
      if (this.semaphore) {
        await new Promise(resolve => setTimeout(resolve, 1));
        return this.postLbasInfo(lbas);
      }

      // 寝ているセマフォを立て、通信後にまた寝かせる
      this.semaphore = true;
      const endpoint = 'lbas-info';
      const result = await this.http.post<{}>(this.serverUrl + '/' + endpoint,
        JSON.stringify(lbas)
      ).toPromise();
      this.semaphore = false;

      return result;
    } catch (e) {
      console.log(e);
      return {};
    }
  }

  /**
   * /own-fleet-infoエンドポイント
   * @param own 自艦隊
   */
  public async postOwnInfo(own: {}): Promise<{}> {
    try {
      // セマフォが立っている際は、何かしらの通信中なので、読み込みを待機する
      if (this.semaphore) {
        await new Promise(resolve => setTimeout(resolve, 1));
        return this.postOwnInfo(own);
      }

      // 寝ているセマフォを立て、通信後にまた寝かせる
      this.semaphore = true;
      const endpoint = 'own-fleet-info';
      const result = await this.http.post<{}>(this.serverUrl + '/' + endpoint,
        JSON.stringify(own)
      ).toPromise();
      this.semaphore = false;

      return result;
    } catch (e) {
      console.log(e);
      return {};
    }
  }
}
