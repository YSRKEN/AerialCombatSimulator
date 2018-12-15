import java.util.List;

import lombok.Data;

@Data
public class FleetData {
	private String name;
	private List<WeaponData> weapon;
}
