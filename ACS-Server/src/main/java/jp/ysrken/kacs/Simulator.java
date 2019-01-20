package jp.ysrken.kacs;

import java.util.HashMap;
import java.util.Map;

import jp.ysrken.kacs.model.SimulationData;

public class Simulator {
	/**
	 * シミュレーションを実施する
	 * @param simulationData 基地航空隊・敵艦隊・自艦隊のデータ
	 * @param type シミュレーションの種類
	 * @param loop_count 反復回数
	 * @return
	 */
	public static Map<String, Object> simulation(SimulationData simulationData, SimulationMode type, int loop_count) {
		Map<String, Object> result = new HashMap<>();
		
		// 敵の制空値分布を算出する
		Map<Integer, Integer> antiAirValueDict = new HashMap<>();
		
		for(int i = 0; i < loop_count; ++i) {
			
		}
		result.put("EnemyAntiAirValue", antiAirValueDict);
		return result;
	}
}
