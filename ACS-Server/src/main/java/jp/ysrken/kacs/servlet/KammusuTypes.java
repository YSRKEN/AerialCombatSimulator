package jp.ysrken.kacs.servlet;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

import jp.ysrken.kacs.DatabaseService;

@SuppressWarnings("serial")
@WebServlet(name = "KammusuTypes", urlPatterns = { "/kammusu-types" })
public class KammusuTypes extends HttpServlet {
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
		String short_name_flg = request.getParameter("short_name_flg");
		System.out.println("/kammusu-types?short_name_flg=" + short_name_flg);
		
		// クエリを実行する
		String tempQuery = (short_name_flg != null && short_name_flg.equals("1") ? "short_name as name" : "name");

		List<Map<String, Object>> result = database.select("SELECT id, " + tempQuery + " FROM kammusu_type ORDER BY id");
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(result));
	}
}

