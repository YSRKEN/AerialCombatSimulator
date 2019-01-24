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
	 * 制空値を計算して返す
	 * @param lbasFlg 基地航空隊の場合はtrue
	 * @return 制空値
	 */
	public Integer calcAntiAirValue() {
		for (WeaponData w : weapon) {
			w.refresh();
		}
		return weapon.stream().mapToInt(w -> w.calcAntiAirValue(true)).sum();
	}
}
