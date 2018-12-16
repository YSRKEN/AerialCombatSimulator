package jp.ysrken.kacs.servlet;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

import jp.ysrken.kacs.model.RequestData;
import jp.ysrken.kacs.model.SimulationData;

@SuppressWarnings("serial")
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
		
		// リクエストボディからJSON部分を取り出し、オブジェクトに変更
		ObjectMapper mapper = new ObjectMapper();
		BufferedReader reader = request.getReader();
		SimulationData simulationData = 
			mapper.readValue(request.getReader(), SimulationData.class);

		// シミュレーション処理を行う
		Map<String, Object> result = new HashMap<>();
		result.put("type", Integer.parseInt(type));
		result.put("field1", "hoge");
		result.put("field2", 3.14);
		result.put("field3", simulationData.hashCode());
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		response.getWriter().println(mapper.writeValueAsString(result));
		return;
	}
}
