import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SaveDataService {

  constructor() {}

  /**
   * 文字列をセーブする
   * @param key キー
   * @param value 文字列
   */
  saveString(key: string, value: string) {
    window.localStorage.setItem(key, value);
  }

  /**
   * 文字列をロードする
   * @param key キー
   * @return 文字列
   */
  loadString(key: string, defaultValue: string = ''): string {
    const rawValue = window.localStorage.getItem(key);
    return rawValue == null ? defaultValue : rawValue;
  }

  /**
   * 数値をセーブする
   * @param key キー
   * @param value 数値
   */
  saveNumber(key: string, value: number) {
    window.localStorage.setItem(key, value.toString(10));
  }

  /**
   * 数値を浮動小数点数としてロードする
   * @param key キー
   * @param value 数値
   */
  loadFloat(key: string, defaultValue: number = NaN): number {
    const rawValue = window.localStorage.getItem(key);
    return rawValue == null ? defaultValue : parseFloat(rawValue);
  }

  /**
   * 数値を整数としてロードする
   * @param key キー
   * @param value 数値
   */
  loadInt(key: string, defaultValue: number = NaN): number {
    const rawValue = window.localStorage.getItem(key);
    return rawValue == null ? defaultValue : parseInt(rawValue);
  }

  /**
   * 真偽値をセーブする
   * @param key キー
   * @param value 数値
   */
  saveBoolean(key: string, value: boolean) {
    window.localStorage.setItem(key, value ? 'true' : 'false');
  }

  /**
   * 真偽値をロードする
   * 参考：
   * converting String true/false to Boolean value [duplicate]
   * https://stackoverflow.com/questions/3976714/converting-string-true-false-to-boolean-value
   * @param key キー
   * @param value 数値
   */
  loadBoolean(key: string): boolean {
    return window.localStorage.getItem(key).toLowerCase() === 'true';
  }

  /**
   * オブジェクトをセーブする
   * @param key キー
   * @param value オブジェクト
   */
  saveObject<T>(key: string, value: T){
    window.localStorage.setItem(key, JSON.stringify(value));
  }

  /**
   * オブジェクトをロードする
   * @param key キー
   * @return オブジェクト
   */
  loadObject<T>(key: string, defaultValue: T = null): T{
    const rawValue = window.localStorage.getItem(key);
    return rawValue == null ? defaultValue : JSON.parse(rawValue);
  }
}
