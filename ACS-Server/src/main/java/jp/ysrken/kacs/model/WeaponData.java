package jp.ysrken.kacs.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
public class WeaponData {
	private String name;
	private String rf;
	private String mas;
	@JsonProperty("slot_count")
	private String slotCount;
}
