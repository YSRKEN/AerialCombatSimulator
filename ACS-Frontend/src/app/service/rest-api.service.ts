import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

/**
 * valueとnameのペアを持つインターフェース
 */
export type ValueNamePair = { "value": string, "name": string };

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
        return this.cache[key];
      }

      // セマフォが立っている際は、何かしらの通信中なので、読み込みを待機する
      if (this.semaphore) {
        await new Promise(resolve => setTimeout(resolve, 100));
        return this.getRequest<T>(key, endpoint);
      }

      // 寝ているセマフォを立て、通信後にまた寝かせる
      // 
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
   */
  public async getWeaponTypes(): Promise<ValueNamePair[]> {
    // 結果を取得する
    const result = await this.getRequest<ValueNamePair[]>('getWeaponTypes', 'weapon-types');

    // 失敗時の処理
    if (result === null) {
      return [];
    }

    // 成功時の処理
    return result;
  }
}
