package jp.ysrken.kacs;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

@WebServlet(name = "KammusuNames", urlPatterns = { "/kammusu-names" })
public class KammusuNames extends HttpServlet {
	/**
	 * 一意なバージョンID
	 */
	private static final long serialVersionUID = 2L;

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
		String type = request.getParameter("type");
		String kammusu_flg = request.getParameter("kammusu_flg");
		System.out.println("/kammusu-names?type=" + type + "&kammusu_flg=" + kammusu_flg);
		
		// クエリを実行する
		String tempQuery1 = (kammusu_flg != null ? "WHERE kammusu_flg='" + kammusu_flg + "' " : "");
		String tempQuery2 = (kammusu_flg != null ? "AND kammusu_flg='" + kammusu_flg + "' " : "");

		List<Map<String, Object>> result;
		if (type == null){
			result = database.select("SELECT id, name, slotsize, slot1, slot2, slot3, slot4, slot5 FROM kammusu " + tempQuery1 + "ORDER BY id");
		} else {
			result = database.select("SELECT id, name, slotsize, slot1, slot2, slot3, slot4, slot5 FROM kammusu WHERE type = '" + type + "' " + tempQuery2 + "ORDER BY id");
		}
		
		// 返却用に加工を施す
		List<Map<String, Object>> result2 = new ArrayList<>();
		for(Map<String, Object> pair : result) {
			Map<String, Object> temp = new HashMap<>();
			temp.put("id", pair.get("id"));
			temp.put("name", pair.get("name"));
			int slotsize = (Integer) pair.get("slotsize");
			List<Integer> slot = new ArrayList<>();
			for (int i = 0; i < slotsize; ++i) {
				slot.add((Integer) pair.get(String.format("slot%d", i + 1)));
			}
			temp.put("slot", slot);
			result2.add(temp);
		}
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(result2));
	}
}
