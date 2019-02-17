package jp.ysrken.kacs;

import java.util.*;

import jp.ysrken.kacs.model.*;
import lombok.Getter;

public class Simulator {
	/**
	 * 自分自身の唯一のインスタンス
	 */
	@Getter
	private static Simulator simulator = null;

	private Random random = null;

	/**
	 * 基地航空隊における、各部隊ごとの制空値を計算する
	 * @param lbasList 基地航空隊の一覧
	 * @return 各部隊ごとの制空値
	 */
	private List<List<Integer>> calcLbasAntiAirValue(List<LbasData> lbasList) {
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
	 * 制空結果を判定する
	 * @param friendAntiAirValue 味方の制空値
	 * @param enemyAntiAirValue 敵の制空値
	 * @return 制空結果
	 */
	private int judgeAirStatus(int friendAntiAirValue, int enemyAntiAirValue) {
		if (friendAntiAirValue >= enemyAntiAirValue * 3) {
			return 0;
		}
		if (friendAntiAirValue * 2 >= enemyAntiAirValue * 3) {
			return 1;
		}
		if (friendAntiAirValue * 3 > enemyAntiAirValue * 2) {
			return 2;
		}
		if (friendAntiAirValue * 3 > enemyAntiAirValue) {
			return 3;
		}
		return 4;
	}

	// St1撃墜用のメモ。killedSlot[搭載数][制空状況]＝[可能性の一覧]
	private List<List<List<Integer>>> killedSlot;

	// St1撃墜用のメモを事前計算する
	private void calcKilledSlot() {
		// 制空定数
		int[] awStatusCoeff = new int[] { 1, 3, 5, 7, 10 };

		// 最大搭載数
		int MAX_SLOT_SIZE = 300;

		// 事前計算
		killedSlot = new ArrayList<>();
		for (int slot = 0; slot <= MAX_SLOT_SIZE; ++slot) {
			List<List<Integer>> list1 = new ArrayList<>();
			for (int aws = 0; aws < 5; ++aws) {
				List<Integer> list2 = new ArrayList<>();
				for (int i = 0; i <= 11 - awStatusCoeff[aws]; ++i) {
					for (int j = 0; j <= 11 - awStatusCoeff[aws]; ++j) {
						list2.add(slot - slot * (35 * i + 65 * j) / 1000);
					}
				}
				list1.add(list2);
			}
			killedSlot.add(list1);
		}
	}

	private void st1DestroyForEnemy(List<List<Integer>> slotCount, int status) {
		for (List<Integer> integer : slotCount) {
			for (int j = 0; j < integer.size(); ++j) {
				List<Integer> candidate = killedSlot.get(integer.get(j)).get(status);
				integer.set(j, candidate.get(random.nextInt(candidate.size())));
			}
		}
	}

	private Simulator() {
		calcKilledSlot();
		random = new Random();
	}

	/**
	 * インスタンスを初期化する
	 */
	public static void initialize() {
		if (simulator != null) {
			return;
		}
		simulator = new Simulator();
	}

	/**
	 * シミュレーションを実施する
	 * @param simulationData 基地航空隊・敵艦隊・自艦隊のデータ
	 * @param type シミュレーションの種類
	 * @param loop_count 反復回数
	 * @return
	 */
	public Map<String, Object> simulation(SimulationData simulationData, SimulationMode type, int loop_count) {
		Map<String, Object> result = new HashMap<>();

		// 基地航空隊の制空値を算出する
		List<List<Integer>> lbasAntiAirValue = calcLbasAntiAirValue(simulationData.getLbas());
		result.put("LbasAntiAirValue", lbasAntiAirValue);

		// 基地航空隊＋本隊の制空状況をカウントするための配列を用意する
		List<List<Integer>> lbasStatusCount = new ArrayList<>();
		if (type != SimulationMode.Main) {
			for (int i = 0; i < lbasAntiAirValue.size(); ++i) {
				for (int j = 0; j < lbasAntiAirValue.get(i).size(); ++j) {
					lbasStatusCount.add(Arrays.asList(0, 0, 0, 0, 0));
				}
			}
		}
		if (type != SimulationMode.LBAS) {
			lbasStatusCount.add(Arrays.asList(0, 0, 0, 0, 0));
		}

		// 本隊の制空値を算出する
		simulationData.getOwn().refresh();
		int ownAntiAirValue1 = simulationData.getOwn().calcAntiAirValue(true);
		int ownAntiAirValue2 = simulationData.getOwn().calcAntiAirValue(false);
		result.put("OwnAntiAirValue1", ownAntiAirValue1);
		result.put("OwnAntiAirValue2", ownAntiAirValue2);

		// 敵の編成を検索する
		SearcherService searcher = SearcherService.getInstance();
		EnemyData enemyData = simulationData.getEnemy();
		OwnData enemyFleetData = searcher.findFromEnemyData(enemyData.getMap(), enemyData.getPoint());
		result.put("enemyFleetData", enemyFleetData.toString());
		List<List<Integer>> enemySlotCount = enemyFleetData.getSlotCount();

		// 敵の制空値分布を算出する
		Map<Integer, Integer> antiAirValueDict = new HashMap<>();
		for(int i = 0; i < loop_count; ++i) {
			enemyFleetData.setSlotCount(enemySlotCount);

			// 基地航空隊による撃墜
			if (type != SimulationMode.Main) {
				int j = 0;
				for (List<Integer> lbas : lbasAntiAirValue) {
					for (int lbas2 : lbas) {
						// 敵の制空値を割り出す
						int enemyAntiAirValue = enemyFleetData.calcAntiAirValue(true);

						// St1撃墜する
						int status = judgeAirStatus(lbas2, enemyAntiAirValue);
						List<List<Integer>> enemySlotCount_ = enemyFleetData.getSlotCount();
						st1DestroyForEnemy(enemySlotCount_, status);
						enemyFleetData.setSlotCount(enemySlotCount_);

						// カウントを追加する
						lbasStatusCount.get(j).set(status, lbasStatusCount.get(j).get(status) + 1);
						++j;
					}
				}
			}

			// 連想配列に追加
			int enemyAntiAirValue = enemyFleetData.calcAntiAirValue(false);
			if (antiAirValueDict.containsKey(enemyAntiAirValue)) {
				antiAirValueDict.put(enemyAntiAirValue, antiAirValueDict.get(enemyAntiAirValue) + 1);
			} else {
				antiAirValueDict.put(enemyAntiAirValue, 1);
			}

			// 本隊による攻撃
			if (type != SimulationMode.LBAS) {
				// 制空状況のカウントを追加する
				int status = judgeAirStatus(ownAntiAirValue2, enemyAntiAirValue);
				lbasStatusCount.get(lbasStatusCount.size() - 1).set(status, lbasStatusCount.get(lbasStatusCount.size() - 1).get(status) + 1);

				// St1撃墜する
				List<List<Integer>> enemySlotCount_ = enemyFleetData.getSlotCount();
				st1DestroyForEnemy(enemySlotCount_, status);
				enemyFleetData.setSlotCount(enemySlotCount_);

				// St2撃墜する
				for(FleetData fleet : enemyFleetData.getFleet()) {
					for(WeaponData weapon : fleet.getWeapon()) {
						if (weapon.isAttackPlane()) {

						}
					}
				}
			}
		}
		result.put("EnemyAntiAirValue", antiAirValueDict);
		result.put("LbasStatus", lbasStatusCount);
		return result;
	}
}
