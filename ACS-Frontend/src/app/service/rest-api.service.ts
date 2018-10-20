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

  private serverUrl = "http://localhost:8080";

  constructor(private http: HttpClient) {
    if (window.location.href.indexOf("localhost") < 0){
      this.serverUrl = "https://aerial-combat-service.appspot.com";
    }
  }

  /**
   * weapon-typesエンドポイント
   */
  public async getWeaponTypes(): Promise<ValueNamePair[]> {
    try {
      return await this.http.get<ValueNamePair[]>(this.serverUrl + '/weapon-types').toPromise();
    } catch (e) {
      console.log(e);
      return [];
    }
  }
}
