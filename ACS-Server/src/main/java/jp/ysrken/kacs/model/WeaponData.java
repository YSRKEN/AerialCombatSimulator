package jp.ysrken.kacs.model;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

import jp.ysrken.kacs.DatabaseService;
import lombok.Data;

@Data
public class WeaponData {
	/**
	 * 装備名
	 */
	private int id;
	
	/**
	 * 装備種
	 */
	private int type;
	
	/**
	 * 改修値
	 */
	private int rf;
	
	/**
	 * 艦載機熟練度
	 */
	private int mas;
	
	/**
	 * 搭載数
	 */
	@JsonProperty("slot_count")
	private int slotCount;

	/**
	 * 対空値
	 */
	@JsonIgnore
	private int aa;
	
	/**
	 * 命中値
	 */
	@JsonIgnore
	private int accuracy;
	
	/**
	 * 迎撃値
	 */
	@JsonIgnore
	private int interception;
	
	/**
	 * 戦闘行動半径
	 */
	@JsonIgnore
	private int radius;
	
	/**
	 * POJOとして与えられたデータを元に、他の情報を復元する
	 */
	public void refresh() {
		DatabaseService db = DatabaseService.getDatabase();
		Map<String, Object> result = db.select("SELECT type, aa, accuracy, interception, radius FROM weapon WHERE id=? LIMIT 1", id).get(0);
		type = (Integer) result.get("type");
		aa = (Integer) result.get("aa");
		accuracy = (Integer) result.get("accuracy");
		interception = (Integer) result.get("interception");
		radius = (Integer) result.get("radius");
	}
	
	/**
	 * 制空値を計算して返す
	 * @param lbasFlg 基地航空隊の場合はtrue
	 * @return 制空値
	 */
	public int calcAntiAirValue(boolean lbasFlg) {
		// 艦載機じゃない場合は制空値を計算しない
		if (type <= 6) return 0;
		if (type == 17) return 0;
		if (19 <= type && type <= 30) return 0;
		if (34 <= type) return 0;
		if (!lbasFlg) {
			if (12 <= type && type <= 13) return 0;
			if (type == 16 || type == 18 || type == 31) return 0;
		}
		
		// 外部熟練度を内部熟練度に変換する
		final int[] masTable = {0, 10, 25, 40, 55, 70, 80, 100, 120};
		final int[] pfTable = {0, 0, 2, 5, 9, 14, 14, 22, 22};
		final int[] wbTable = {0, 0, 1, 1, 1, 3, 3, 6, 6};
		
		// 制空値を計算する
		switch(type) {
		case 7:
		case 14:
		case 32:
		case 33:
			// 艦戦 or 水戦 or 陸戦 or 局戦
			return (int)((aa + 0.2 * rf) * Math.sqrt(slotCount) + Math.sqrt(masTable[mas] / 10.0) + pfTable[mas]);
		case 9:
			// 爆戦
			return (int)((aa + 0.25 * rf) * Math.sqrt(slotCount) + Math.sqrt(masTable[mas]));
		case 15:
			// 水爆
			return (int)(aa * Math.sqrt(slotCount) + Math.sqrt(masTable[mas]) + wbTable[mas]);
		case 8:
		case 10:
		case 11:
			// 艦攻 or 艦爆 or 噴式
			return (int)(aa * Math.sqrt(slotCount) + Math.sqrt(masTable[mas]));
		case 12:
		case 13:
		case 16:
		case 18:
		case 31:
			if (!lbasFlg) return 0;
			return (int)(aa * Math.sqrt(slotCount) + Math.sqrt(masTable[mas]));
		default:
			return 0;
		}
	}
}
