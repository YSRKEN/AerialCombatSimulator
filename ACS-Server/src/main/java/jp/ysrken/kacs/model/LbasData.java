package jp.ysrken.kacs.model;

import java.util.List;
import java.util.stream.Collectors;

import lombok.Data;

@Data
public class LbasData {
	/**
	 * 攻撃回数
	 */
	private int count;

	/**
	 * 基地航空隊の装備
	 */
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
	 * @return 制空値
	 */
	public Integer calcAntiAirValue() {
		for (WeaponData w : weapon) {
			w.refresh();
		}
		return weapon.stream().mapToInt(w -> w.calcAntiAirValue(true)).sum();
	}
}
