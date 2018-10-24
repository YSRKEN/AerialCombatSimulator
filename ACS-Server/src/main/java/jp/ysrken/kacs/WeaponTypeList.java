package jp.ysrken.kacs;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

@WebServlet(name = "WeaponTypeList", urlPatterns = { "/weapon-types" })
public class WeaponTypeList extends HttpServlet {
	/**
	 * 一意なバージョンID
	 */
	private static final long serialVersionUID = 1L;

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
		String category = request.getParameter("category");
		String short_name_flg = request.getParameter("short_name_flg");
		
		// クエリを実行する
		List<Map<String, Object>> result;
		if (category == null || category.equals("Normal")){
			if (short_name_flg != null && short_name_flg.equals("1")) {
				result = database.select("SELECT id, short_name as name FROM weapon_type ORDER BY id");
			}else {
				result = database.select("SELECT id, name FROM weapon_type ORDER BY id");
			}
		} else {
			if (short_name_flg != null && short_name_flg.equals("1")) {
				String query = "SELECT id, short_name as name FROM weapon_type WHERE weapon_type.name IN (SELECT type FROM weapon_category WHERE category=?) ORDER BY id";
				result = database.select(query, category);
			}else {
				String query = "SELECT id, name FROM weapon_type WHERE name IN (SELECT type FROM weapon_category WHERE category=?) ORDER BY id";
				result = database.select(query, category);
			}
		}
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(result));
	}
}

