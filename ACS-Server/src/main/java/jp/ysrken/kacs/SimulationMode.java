package jp.ysrken.kacs;

import java.util.Arrays;

/**
 * シミュレーションの実行モードを設定する
 * @author ysrken
 */
public enum SimulationMode {
	All(0),  // 全て
	LBAS(1),  // 基地航空隊
	Main(2);  // 本隊
	
	private int value;
	
	SimulationMode(int value) {
		this.value = value;
	}
	
	public static SimulationMode fromInt(int value) {
		return Arrays.stream(SimulationMode.values()).filter(x -> x.value == value).findFirst().orElse(SimulationMode.All);
	}
}
