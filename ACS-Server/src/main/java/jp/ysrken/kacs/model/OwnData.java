package jp.ysrken.kacs.model;

import java.util.ArrayList;
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

	/**
	 * POJOとして与えられたデータを元に、他の情報を復元する
	 */
	public void refresh() {
		for (FleetData fleetData : fleet) {
			fleetData.refresh();
		}
	}

	@Override
	public String toString() {
		StringBuffer buffer = new StringBuffer();
		// 陣形
		buffer.append(String.format("%s%n", this.getFormation()));

		// 艦隊情報
		for (int index = 0; index < this.getFleet().size(); ++index) {
			FleetData fleet = this.getFleet().get(index);

			// 艦隊番号
			buffer.append(String.format("(%d)", index + 1));

			// 艦名
			buffer.append(fleet.getName());

			// 装備情報
			List<String> temp = new ArrayList<>();
			fleet.getWeapon().forEach(weapon -> {
				weapon.refresh();
				temp.add(String.format("[%d]%s", weapon.getSlotCount(), weapon.getName()));
			});
			buffer.append(String.format("　%s%n", String.join(",", temp)));
		}

		return buffer.toString();
	}
}
