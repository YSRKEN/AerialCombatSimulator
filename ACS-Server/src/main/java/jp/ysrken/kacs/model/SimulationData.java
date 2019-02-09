package jp.ysrken.kacs.model;

import java.util.List;

import lombok.Data;

@Data
public class SimulationData {
	private List<LbasData> lbas;
	private EnemyData enemy;
	private OwnData own;
}
