package jp.ysrken.kacs.servlet;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.Map;
import java.util.stream.Collectors;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import jp.ysrken.kacs.model.RequestData;
import jp.ysrken.kacs.model.SimulationData;

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
		
		// リクエストボディからJSON部分を取り出す
		ObjectMapper mapper = new ObjectMapper();
		String requestBody = request.getReader().lines().collect(Collectors.joining(""));
		RequestData temp = mapper.readValue(requestBody, RequestData.class);
		String jsonData = temp.getParams();

		// JSONをオブジェクトに変更
		SimulationData simulationData = 
			mapper.readValue(jsonData, SimulationData.class);
		return;
	}
}
