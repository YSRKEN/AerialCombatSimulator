import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Simulation {
	public static void main(String[] args) {
		try {
			List<String> lines = Files.readAllLines(new File("sample.json").toPath(), StandardCharsets.UTF_8);
			String reqJson = String.join("\n", lines);
			ObjectMapper mapper = new ObjectMapper();
			RequestData reqMap = mapper.readValue(reqJson, RequestData.class);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return;
	}
}
