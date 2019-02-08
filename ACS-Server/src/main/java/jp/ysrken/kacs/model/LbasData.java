package jp.ysrken.kacs.model;

import java.util.Comparator;
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
		int rawAAV = weapon.stream().mapToInt(w -> w.calcAntiAirValue(true)).sum();
		if (weapon.stream().anyMatch(w -> w.getType() == 36)) {
			return (int)(1.15 * rawAAV);
		} else {
			return rawAAV;
		}
	}

	/**
	 * 戦闘行動半径を計算する
	 * @return 戦闘行動半径
	 */
	public int calcRadius() {
		/**
		 * 航空隊の最低戦闘行動半径
		 */
		int minRadius = weapon.stream().map(WeaponData::getRadius).min(Comparator.naturalOrder()).orElse(0);

		/**
		 * 航空隊の偵察機の最大戦闘行動半径
		 */
		int maxRadius = weapon.stream().filter(WeaponData::isRecon).map(WeaponData::getRadius).min(Comparator.naturalOrder()).orElse(0);
		if (maxRadius <= minRadius) {
			return minRadius;
		}else {
			return (int)Math.min(minRadius + Math.round(Math.sqrt(maxRadius - minRadius)), minRadius + 3);
		}
	}
}
