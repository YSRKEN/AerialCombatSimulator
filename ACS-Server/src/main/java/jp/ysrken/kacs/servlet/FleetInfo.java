package jp.ysrken.kacs.servlet;

import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

import jp.ysrken.kacs.DatabaseService;
import jp.ysrken.kacs.SearcherService;
import jp.ysrken.kacs.model.FleetData;
import jp.ysrken.kacs.model.OwnData;

@SuppressWarnings("serial")
@WebServlet(name = "FleetInfo", urlPatterns = { "/fleet-info" })
public class FleetInfo extends HttpServlet {
	/**
	 * マップのURLを返す
	 */
	@Override
	public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {

		// データベースを確認する
		SearcherService.initialize(getServletContext());
		SearcherService searcher = SearcherService.getInstance();
		if (searcher == null) {
			response.sendError(500);
			return;
		}
		
		// パラメーターを確認する
		String map = request.getParameter("map");
		String point = request.getParameter("point");
		String level = request.getParameter("level");
		System.out.println("/fleet-info?map=" + map + "&point=" + point + "&level=" + level);

		// クエリを実行する(指定した条件の敵艦一覧を取り出す)
		Map<String, Object> res = new LinkedHashMap<>();
		if (map == null || point == null || level == null) {
		} else {
			StringBuffer buffer = new StringBuffer();
			OwnData enemyFleets = searcher.findFromEnemyData(map, point);
			buffer.append("制空値：" + enemyFleets.calcAntiAirValue(true) + " / " + enemyFleets.calcAntiAirValue(false) + "\n");
			buffer.append(enemyFleets.toString());
			res.put("text", buffer.toString());
			res.put("aav1", enemyFleets.calcAntiAirValue(true));
			res.put("aav2", enemyFleets.calcAntiAirValue(false));
		}

		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(res));
	}
}
