package jp.ysrken.kacs.model;

import jp.ysrken.kacs.DatabaseService;
import lombok.Data;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Data
public class FleetData {
	private String id;
	private int aa;
	private int attack;
	private int torpedo;
	private String name;
	private List<WeaponData> weapon;

	/**
	 * POJOとして与えられたデータを元に、他の情報を復元する
	 */
	public void refresh() {
		for (WeaponData weaponData : weapon) {
			weaponData.refresh();
		}
		DatabaseService db = DatabaseService.getDatabase();
		Map<String, Object> result = db.select("SELECT name, aa, attack, torpedo FROM kammusu WHERE id=? LIMIT 1", id).get(0);
		name = (String) result.get("name");
		aa = (Integer) result.get("aa");
		attack = (Integer) result.get("attack");
		torpedo = (Integer) result.get("torpedo");
	}

	/**
	 * スロットの搭載数一覧
	 * @return スロットの搭載数一覧
	 */
	public List<Integer> getSlotCount() {
		return weapon.stream().map(WeaponData::getSlotCount).collect(Collectors.toList());
	}

	/**
	 * スロットの搭載数一覧をセットする
	 * @param slotCount スロットの搭載数一覧
	 */
	public void setSlotCount(List<Integer> slotCount) {
		int weaponSize = weapon.size();
		for (int i = 0; i < weaponSize; ++i) {
			weapon.get(i).setSlotCount(slotCount.get(i));
		}
	}

	/**
	 * St1撃墜される可能性がある一覧を返す
	 * @return 一覧
	 */
	public List<Boolean> getSt1Flg() {
		return weapon.stream().map(WeaponData::getSt1Flg).collect(Collectors.toList());
	}

	/**
	 * 制空値を計算して返す
	 * @param lbasFlg 基地航空隊関係ならtrue
	 * @return 制空値
	 */
	public Integer calcAntiAirValue(boolean lbasFlg) {
		return weapon.stream().mapToInt(w -> w.calcAntiAirValue(lbasFlg)).sum();
	}

	/**
	 * 加重対空値を計算する
	 * @return 加重対空値
	 */
	public double calcWeightedAntiAir() {
		double weightedAntiAir = aa + weapon.stream().mapToDouble(WeaponData::getWeightedAntiAir).sum();
		int a = weapon.stream().anyMatch(w -> w.getId() != 0) ? 2 : 1;
		return a * (int)(weightedAntiAir / a);
	}

	/**
	 * 艦隊防空値を計算する
	 * @return 艦隊防空値
	 */
	public double calcAntiAirBonus() {
		return (int)(weapon.stream().mapToDouble(WeaponData::getAntiAirBonus).sum());
	}
}
