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

import jp.ysrken.kacs.DatabaseService;
import jp.ysrken.kacs.SearcherService;
import jp.ysrken.kacs.SimulationMode;
import jp.ysrken.kacs.Simulator;
import jp.ysrken.kacs.model.RequestData;
import jp.ysrken.kacs.model.SimulationData;

@SuppressWarnings("serial")
@WebServlet(name = "Simulation", urlPatterns = { "/simulation" })
public class Simulation extends HttpServlet {
	/**
	 * シミュレーションする回数
	 */
	private static int LOOP_COUNT = 10000;
	
	/**
	 * シミュレーションを行い、結果を返す
	 */
	@Override
	public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
		// データベースを確認する
		SearcherService.initialize(getServletContext());
		if (SearcherService.getInstance() == null) {
			response.sendError(500);
			return;
		}
		
		// POSTされた各種データを確認する
		//シミュレーションの種類(0→全部、1→基地航空隊vs敵艦隊、2→自艦隊vs敵艦隊)
		SimulationMode type = SimulationMode.All;
		if (request.getParameter("type") != null) {
			type = SimulationMode.fromInt(Integer.parseInt(request.getParameter("type")));
		}
		//基地航空隊・敵艦隊・自艦隊の情報
		BufferedReader reader = request.getReader();
		
		// リクエストボディからJSON部分を取り出し、オブジェクトに変更
		ObjectMapper mapper = new ObjectMapper();
		SimulationData simulationData = 
			mapper.readValue(reader, SimulationData.class);

		// シミュレーション処理を行う
		Simulator.initialize();
		Simulator simulator = Simulator.getSimulator();
		Map<String, Object> result = simulator.simulation(simulationData, type, LOOP_COUNT);

		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		response.getWriter().println(mapper.writeValueAsString(result));
		return;
	}
}
