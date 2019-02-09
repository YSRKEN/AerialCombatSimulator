package jp.ysrken.kacs.model;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import lombok.Data;

@Data
public class FleetData {
	private String name;
	private List<WeaponData> weapon;

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
}
