package jp.ysrken.kacs.servlet;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.Map;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

@WebServlet(name = "Simulation", urlPatterns = { "/simulation" })
public class Simulation extends HttpServlet {
	/**
	 * シミュレーションを行い、結果を返す
	 */
	@Override
	public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
		// POSTされた各種データを確認する
		String type = request.getParameter("type");
		if (type == null) {
			type = "1";
		}
		BufferedReader buffer = new BufferedReader(request.getReader());
		String reqJson = buffer.readLine();

		// JSONをオブジェクトに変更
		ObjectMapper mapper = new ObjectMapper();
		Map<String, Object> reqMap = 
			mapper.readValue(reqJson, new TypeReference<Map<String, Object>>() {});
		String params = (String) reqMap.get("params");
		reqMap = 
				mapper.readValue(params, new TypeReference<Map<String, Object>>() {});
		return;
	}
}
