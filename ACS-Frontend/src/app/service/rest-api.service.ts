import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class RestApiService {

  /**
   * アクセスする先のサーバーアドレス
   */
  private serverUrl = "http://localhost:8080";

  /**
   * データキャッシュ
   */
  private cache :{[key: string]: any; } = {};

  /**
   * セマフォ
   */
  private semaphore: boolean = false;

  /**
   * コンストラクタ
   * @param http HTTPクライアント
   */
  constructor(private http: HttpClient) {
    // ローカルサーバーで動いていない際は、本番用serverにアクセスするようにする
    if (window.location.href.indexOf("localhost") < 0){
      this.serverUrl = "https://aerial-combat-service.appspot.com";
    }
  }

  /**
   * キャッシュ機能を含んだGETクライアント
   * @param key キャッシュのキー
   * @param endpoint エンドポイントURL
   */
  private async getRequest<T>(key: string, endpoint: string): Promise<T | null> {
    try {
      // キャッシュに存在する場合はそちらを返却する
      if (key in this.cache){
        console.log("[cache] " + key);
        return this.cache[key];
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
      this.cache[key] = result;  // キャッシュにデータを追加
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
}
