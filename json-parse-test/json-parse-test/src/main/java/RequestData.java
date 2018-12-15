import java.util.Map;

import lombok.Data;

@Data
public class RequestData {
	private Map<String, String> headers;
	private SimulationData params;
}
