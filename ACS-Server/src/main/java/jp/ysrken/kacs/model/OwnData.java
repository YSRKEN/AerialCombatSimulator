package jp.ysrken.kacs.model;

import java.util.List;
import java.util.stream.Collectors;

import lombok.Data;

@Data
public class OwnData {
	private String formation;
	private List<FleetData> fleet;

	/**
	 * スロットの搭載数一覧
	 * @return スロットの搭載数一覧
	 */
	public List<List<Integer>> getSlotCount() {
		return fleet.stream().map(FleetData::getSlotCount).collect(Collectors.toList());
	}

	/**
	 * スロットの搭載数一覧をセットする
	 * @param slotCount スロットの搭載数一覧
	 */
	public void setSlotCount(List<List<Integer>> slotCount) {
		int fleetSize = fleet.size();
		for (int i = 0; i < fleetSize; ++i) {
			fleet.get(i).setSlotCount(slotCount.get(i));
		}
	}

	/**
	 * 制空値を計算して返す
	 * @param lbasFlg 基地航空隊関係ならtrue
	 * @return 制空値
	 */
	public Integer calcAntiAirValue(boolean lbasFlg) {
		return fleet.stream().mapToInt(f -> f.calcAntiAirValue(lbasFlg)).sum();
	}
}
