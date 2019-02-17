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
	 * 装備ID
	 */
	private int id;
	
	/**
	 * 装備名
	 */
	private String name;
	
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
		Map<String, Object> result = db.select("SELECT name, type, aa, accuracy, interception, radius FROM weapon WHERE id=? LIMIT 1", id).get(0);
		name = (String) result.get("name");
		type = (Integer) result.get("type");
		aa = (Integer) result.get("aa");
		accuracy = (Integer) result.get("accuracy");
		interception = (Integer) result.get("interception");
		radius = (Integer) result.get("radius");
	}

	/**
	 * 艦載機ならtrueを返す
	 * @param lbasFlg 基地航空隊の場合はtrue
	 * @return 艦載機ならtrue
	 */
	public boolean isAirPlane(boolean lbasFlg) {
		switch (WeaponType.of(this.type)){
		case CarrierFighter:
		case CarrierBomber:
		case FighterBomber:
		case Jet:
		case CarrierAttacker:
		case SeaFighter:
		case SeaBomber:
		case LandAttacker:
		case LandFighter1:
		case LandFighter2:
			return true;
		case CarrierReconn:
		case Saiun:
		case SeaReconn:
		case FlyingBoat:
		case LandReconn:
			return lbasFlg;
		default:
			return false;
		}
	}

	/**
	 * 偵察機ならtrueを返す
	 * @return 偵察機ならtrue
	 */
	public boolean isRecon() {
		switch (WeaponType.of(this.type)){
		case CarrierReconn:
		case Saiun:
		case SeaReconn:
		case FlyingBoat:
		case LandReconn:
			return true;
		default:
			return false;
		}
	}

	/**
	 * 制空値を計算して返す
	 * @param lbasFlg 基地航空隊の場合はtrue
	 * @return 制空値
	 */
	public int calcAntiAirValue(boolean lbasFlg) {
		// 艦載機じゃない場合は制空値を計算しない
		if (!this.isAirPlane(lbasFlg)) {
			return 0;
		}
		
		// 外部熟練度を内部熟練度に変換する
		final int[] masTable = {0, 10, 25, 40, 55, 70, 80, 100, 120};
		final int[] pfTable = {0, 0, 2, 5, 9, 14, 14, 22, 22};
		final int[] wbTable = {0, 0, 1, 1, 1, 3, 3, 6, 6};
		
		// 制空値を計算する
		switch(WeaponType.of(this.type)) {
		case CarrierFighter:
		case SeaFighter:
		case LandFighter1:
		case LandFighter2:
			// 艦戦 or 水戦 or 陸戦 or 局戦
			return (int)((aa + 0.2 * rf + (lbasFlg ? interception * 1.5 : 0.0)) * Math.sqrt(slotCount) + Math.sqrt(masTable[mas] / 10.0) + pfTable[mas]);
		case FighterBomber:
			// 爆戦
			return (int)((aa + 0.25 * rf) * Math.sqrt(slotCount) + Math.sqrt(masTable[mas] / 10.0));
		case SeaBomber:
			// 水爆
			return (int)(aa * Math.sqrt(slotCount) + Math.sqrt(masTable[mas] / 10.0) + wbTable[mas]);
		case CarrierBomber:
		case Jet:
		case CarrierAttacker:
			// 艦攻 or 艦爆 or 噴式
			return (int)(aa * Math.sqrt(slotCount) + Math.sqrt(masTable[mas] / 10.0));
		case CarrierReconn:
		case Saiun:
		case SeaReconn:
		case FlyingBoat:
		case LandAttacker:
			if (!lbasFlg) return 0;
			return (int)((aa + interception * 1.5) * Math.sqrt(slotCount) + Math.sqrt(masTable[mas] / 10.0));
		default:
			return 0;
		}
	}
}
