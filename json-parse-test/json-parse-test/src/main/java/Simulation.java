import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Simulation {
	public static void main(String[] args) {
		try {
		    List<String> lines = Files.readAllLines(new File("sample.json").toPath(), StandardCharsets.UTF_8);
			String reqJson = String.join("\n", lines);
			ObjectMapper mapper = new ObjectMapper();
			RequestData reqMap = 
					mapper.readValue(reqJson, RequestData.class);
			RequestData reqMap2 = reqMap;
		} catch (IOException e) {
		    e.printStackTrace();
		}
		return;
	}
}
