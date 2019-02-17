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
		Map<String, Object> result = db.select("SELECT name, aa FROM kammusu WHERE id=? LIMIT 1", id).get(0);
		name = (String) result.get("name");
		aa = (Integer) result.get("aa");
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
		double weightedAntiAir = aa;
		// スタブ
		return weightedAntiAir;
	}
}
