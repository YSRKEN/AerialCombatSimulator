package jp.ysrken.kacs;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import jp.ysrken.kacs.model.EnemyData;
import jp.ysrken.kacs.model.LbasData;
import jp.ysrken.kacs.model.OwnData;
import jp.ysrken.kacs.model.SimulationData;
import jp.ysrken.kacs.model.WeaponData;

public class Simulator {
	/**
	 * 基地航空隊における、各部隊ごとの制空値を計算する
	 * @param lbasList 基地航空隊の一覧
	 * @return 各部隊ごとの制空値
	 */
	private static List<List<Integer>> calcLbasAntiAirValue(List<LbasData> lbasList) {
		List<List<Integer>> result = new ArrayList<>();
		for (LbasData lbas : lbasList) {
			int antiAirValue = lbas.calcAntiAirValue();
			List<Integer> temp = new ArrayList<>();
			for (int i = 0; i < lbas.getCount(); ++i) {
				temp.add(antiAirValue);
			}
			result.add(temp);
		}
		return result;
	}
	
	/**
	 * シミュレーションを実施する
	 * @param simulationData 基地航空隊・敵艦隊・自艦隊のデータ
	 * @param type シミュレーションの種類
	 * @param loop_count 反復回数
	 * @return
	 */
	public static Map<String, Object> simulation(SimulationData simulationData, SimulationMode type, int loop_count) {
		Map<String, Object> result = new HashMap<>();
		
		// 基地航空隊の制空値を算出する
		List<List<Integer>> lbasAntiAirValue = calcLbasAntiAirValue(simulationData.getLbas());
		result.put("LbasAntiAirValue", lbasAntiAirValue);
		
		// 敵の編成を検索する
		SearcherService searcher = SearcherService.getInstance();
		EnemyData enemyData = simulationData.getEnemy();
		OwnData enemyFleetData = searcher.findFromEnemyData(enemyData.getMap(), enemyData.getPoint());
		
		// 敵の制空値分布を算出する
		Map<Integer, Integer> antiAirValueDict = new HashMap<>();
		for(int i = 0; i < loop_count; ++i) {
			
		}
		result.put("EnemyAntiAirValue", antiAirValueDict);
		return result;
	}
}
