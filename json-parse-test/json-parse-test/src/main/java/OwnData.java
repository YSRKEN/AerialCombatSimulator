import java.util.List;

import lombok.Data;

@Data
public class OwnData {
	private String formation;
	private List<FleetData> fleet;
}
