package jp.ysrken.kacs.model;

import lombok.Data;

import java.util.List;

@Data
public class SimulationData {
	private List<LbasData> lbas;
	private EnemyData enemy;
	private OwnData own;
}
