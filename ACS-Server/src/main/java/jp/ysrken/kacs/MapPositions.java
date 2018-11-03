package jp.ysrken.kacs;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

@WebServlet(name = "MapPositions", urlPatterns = { "/map-positions" })
public class MapPositions extends HttpServlet {
	/**
	 * 装備の種類一覧を返す
	 */
	@Override
	public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {

		// データベースを確認する
		DatabaseService.initialize(getServletContext());
		DatabaseService database = DatabaseService.getDatabase();
		if (database == null) {
			response.sendError(500);
			return;
		}
		
		// パラメーターを確認する
		String map = request.getParameter("map");
		System.out.println("/map-positions?map=" + map);
		
		// クエリを実行する
		List<Map<String, Object>> result;
		if (map == null) {
			result = new ArrayList<>();
		}else {
			result = database.select("SELECT DISTINCT(name) FROM position WHERE map=? ORDER BY name", map);
		}
		List<String> result2 = result.stream().map(s -> (String) s.get("name")).collect(Collectors.toList());
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(result2));
	}
}

