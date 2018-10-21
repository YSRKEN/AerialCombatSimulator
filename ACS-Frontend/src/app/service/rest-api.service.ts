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

  constructor(private http: HttpClient) {
    // ローカルサーバーで動いていない際は、本番用serverにアクセスするようにする
    if (window.location.href.indexOf("localhost") < 0){
      this.serverUrl = "https://aerial-combat-service.appspot.com";
    }
  }

  /**
   * weapon-typesエンドポイント
   */
  public async getWeaponTypes(): Promise<ValueNamePair[]> {
    try {
      // キャッシュに存在する場合はそちらを返却する
      if ("getWeaponTypes" in this.cache){
        return this.cache["getWeaponTypes"];
      }

      // セマフォが立っている際は、何かしらの通信中なので、読み込みを待機する
      if (this.semaphore) {
        await new Promise(resolve => setTimeout(resolve, 100));
        return this.getWeaponTypes();
      }

      // 寝ているセマフォを立て、通信後にまた寝かせる
      // 
      this.semaphore = true;
      const result = await this.http.get<ValueNamePair[]>(this.serverUrl + '/weapon-types').toPromise();
      this.semaphore = false;

      // キャッシュにデータを追加する
      this.cache["getWeaponTypes"] = result;

      return result;
    } catch (e) {
      console.log(e);
      return [];
    }
  }
}
