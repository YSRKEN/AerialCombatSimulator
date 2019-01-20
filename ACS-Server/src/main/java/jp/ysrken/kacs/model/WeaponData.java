package jp.ysrken.kacs.model;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

import jp.ysrken.kacs.DatabaseService;
import lombok.Data;

@Data
public class WeaponData {
	/**
	 * 装備名
	 */
	private int id;
	
	/**
	 * 改修値
	 */
	private int rf;
	
	/**
	 * 艦載機熟練度
	 */
	private int mas;
	
	/**
	 * 搭載数
	 */
	@JsonProperty("slot_count")
	private int slotCount;

	/**
	 * 対空値
	 */
	@JsonIgnore
	private int aa;
	
	/**
	 * 命中値
	 */
	@JsonIgnore
	private int accuracy;
	
	/**
	 * 迎撃値
	 */
	@JsonIgnore
	private int interception;
	
	/**
	 * 戦闘行動半径
	 */
	@JsonIgnore
	private int radius;
	
	/**
	 * POJOとして与えられたデータを元に、他の情報を復元する
	 */
	public void refresh() {
		DatabaseService db = DatabaseService.getDatabase();
		List<Map<String, Object>> result = db.select("SELECT aa, accuracy, interception, radius FROM weapon WHERE id=? LIMIT 1", id);
		
	}
}
