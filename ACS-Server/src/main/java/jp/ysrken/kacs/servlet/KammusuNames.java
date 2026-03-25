package jp.ysrken.kacs.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import jp.ysrken.kacs.DatabaseService;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@SuppressWarnings("serial")
@WebServlet(name = "KammusuNames", urlPatterns = { "/kammusu-names" })
public class KammusuNames extends HttpServlet {
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
		
		List<Map<String, Object>> result;
		if (type == null && kammusu_flg == null) {
			result = database.select("SELECT id, name, slotsize, slot1, slot2, slot3, slot4, slot5 FROM kammusu ORDER BY id");
		} else if (type == null) {
			result = database.select(
					"SELECT id, name, slotsize, slot1, slot2, slot3, slot4, slot5 FROM kammusu WHERE kammusu_flg=? ORDER BY id",
					kammusu_flg
			);
		} else if (kammusu_flg == null) {
			result = database.select(
					"SELECT id, name, slotsize, slot1, slot2, slot3, slot4, slot5 FROM kammusu WHERE type=? ORDER BY id",
					type
			);
		} else {
			result = database.select(
					"SELECT id, name, slotsize, slot1, slot2, slot3, slot4, slot5 FROM kammusu WHERE type=? AND kammusu_flg=? ORDER BY id",
					type,
					kammusu_flg
			);
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
