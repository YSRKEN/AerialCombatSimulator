package jp.ysrken.kacs;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.servlet.ServletContext;

import jp.ysrken.kacs.model.FleetData;
import jp.ysrken.kacs.model.OwnData;
import jp.ysrken.kacs.model.WeaponData;
import lombok.Getter;

public class SearcherService {
	/**
	 * 自分自身の唯一のインスタンス
	 */
	@Getter
	private static SearcherService instance = null;
	
	/**
	 * 参照するデータベース
	 */
	private DatabaseService database = null;
	
	/**
	 * クラスを初期化する
	 */
	public static void initialize(ServletContext servletContext) {
		if (instance != null) {
			return;
		}
		instance = new SearcherService();
		DatabaseService.initialize(servletContext);
		instance.database = DatabaseService.getDatabase();
	}
	
	/**
	 * 装備情報を検索して返す(外部熟練度・改修度・搭載数は0がセットされる)
	 * @param id 装備ID
	 * @return 装備情報(存在しない場合は0番の情報が返る)
	 */
	public WeaponData findFromWeaponId(int id) {
		String query = "SELECT * FROM weapon WHERE id=? LIMIT 1";
		List<Map<String, Object>> result = database.select(query, id);
		if (result.size() == 0) {
			return findFromWeaponId(0);
		}
		Map<String, Object> pair = result.get(0);
		
		WeaponData output = new WeaponData();
		output.setId(id);
		output.setName((String) pair.get("name"));
		output.setType((Integer) pair.get("type"));
		output.setRf(0);
		output.setMas(0);
		output.setSlotCount(0);
		output.setAa((Integer) pair.get("aa"));
		output.setAccuracy((Integer) pair.get("accuracy"));
		output.setInterception((Integer) pair.get("interception"));
		output.setRadius((Integer) pair.get("radius"));
		return output;
	}
	
	/**
	 * 艦隊情報を、敵の出現マップと出現マス(場所・n番目・最終編成か否か)で調べる
	 * @param map 出現マップ
	 * @param point 出現マス
	 * @return 艦隊情報(陣形、各艦の名称と装備)
	 */
	public OwnData findFromEnemyData(String map, String point) {
		// 事前準備を実施する
		int finalFlg = point.contains(" (Final)") ? 1 : 0;
		point = point.replace(" (Final)", "");
		String query = "SELECT fc.category AS formation, CASE WHEN unit_index < 6 THEN 1 ELSE 2 END AS index1,\r\n" + 
				"CASE WHEN unit_index < 6 THEN unit_index + 1 ELSE unit_index - 5 END AS index2,\r\n" + 
				"kammusu.name, slotsize, slot1, slot2, slot3, slot4, slot5,\r\n" + 
				"w1.id AS weapon1, w2.id AS weapon2, w3.id AS weapon3,\r\n" + 
				"w4.id AS weapon4, w5.id AS weapon5\r\n" + 
				"FROM position,weapon AS w1,weapon AS w2,weapon AS w3,weapon AS w4,weapon AS w5\r\n" + 
				",formation_category AS fc\r\n" +
				"INNER JOIN kammusu ON kammusu.id = position.enemy\r\n" + 
				"WHERE map=? AND position.name=? AND final_flg=?\r\n" + 
				"AND w1.id = kammusu.weapon1 AND w2.id = kammusu.weapon2\r\n" + 
				"AND w3.id = kammusu.weapon3 AND w4.id = kammusu.weapon4\r\n" + 
				"AND w5.id = kammusu.weapon5 AND fc.id=position.formation\r\n" + 
				"ORDER BY unit_index";
		
		// 検索を行う
		List<Map<String, Object>> result = database.select(query, map, point, finalFlg);
		
		// 検索結果をOwnData型に変換する
		OwnData output = new OwnData();
		output.setFleet(new ArrayList<FleetData>());
		boolean add_formation_flg = false;
		for(Map<String, Object> pair : result) {
			// 陣形
			if (!add_formation_flg) {
				String formation = (String) pair.get("formation");
				output.setFormation(formation);
				add_formation_flg = true;
			}
			
			// 艦船情報
			FleetData fleet = new FleetData();
			String name = (String) pair.get("name");
			fleet.setName(name);
			
			// スロット数
			int slotSize = (Integer)pair.get("slotsize");
			
			// 装備情報
			fleet.setWeapon(new ArrayList<WeaponData>());
			for(int i = 1; i <= slotSize; ++i) {
				int slot = (Integer)pair.get("slot" + i);
				int weaponId = (Integer)pair.get("weapon" + i);
				WeaponData weapon = findFromWeaponId(weaponId);
				weapon.setSlotCount(slotSize);
				fleet.getWeapon().add(weapon);
			}
			output.getFleet().add(fleet);
		}
		return output;
	}
}
