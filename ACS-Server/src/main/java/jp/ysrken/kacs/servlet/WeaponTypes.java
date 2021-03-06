package jp.ysrken.kacs.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import jp.ysrken.kacs.DatabaseService;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import java.util.Map;

@SuppressWarnings("serial")
@WebServlet(name = "WeaponTypes", urlPatterns = { "/weapon-types" })
public class WeaponTypes extends HttpServlet {
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
		System.out.println("/weapon-types?category=" + category + "&short_name_flg=" + short_name_flg);
		
		// クエリを実行する
		String tempQuery1 = (short_name_flg != null && short_name_flg.equals("1") ? "short_name as name" : "name");
		String tempQuery2 = "WHERE weapon_type.name IN (SELECT type FROM weapon_category WHERE category=?)";

		List<Map<String, Object>> result;
		if (category == null || category.equals("Normal")){
			result = database.select("SELECT id, " + tempQuery1 + " FROM weapon_type WHERE name <> 'なし' ORDER BY id");
		} else {
			String query = "SELECT id, " + tempQuery1 + " FROM weapon_type " + tempQuery2 + "ORDER BY id";
			result = database.select(query, category);
		}
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(result));
	}
}

