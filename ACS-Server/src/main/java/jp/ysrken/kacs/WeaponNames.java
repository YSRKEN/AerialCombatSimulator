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

@WebServlet(name = "WeaponNames", urlPatterns = { "/weapon-names" })
public class WeaponNames extends HttpServlet {
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
		String for_kammusu_flg = request.getParameter("for_kammusu_flg");
		
		// クエリを実行する
		String tempQuery1 = (for_kammusu_flg != null ? "WHERE for_kammusu_flg='" + for_kammusu_flg + "' " : "");
		String tempQuery2 = (for_kammusu_flg != null ? "AND for_kammusu_flg='" + for_kammusu_flg + "' " : "");

		List<Map<String, Object>> result;
		if (type == null){
			result = database.select("SELECT id, name FROM weapon " + tempQuery1 + "ORDER BY id");
		} else {
			result = database.select("SELECT id, name FROM weapon WHERE type = '" + type + "' " + tempQuery2 + "ORDER BY id");
		}
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(result));
	}
}
