package jp.ysrken.kacs;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

@SuppressWarnings("serial")
@WebServlet(name = "FleetInfo", urlPatterns = { "/fleet-info" })
public class FleetInfo extends HttpServlet {
	/**
	 * マップのURLを返す
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
		String point = request.getParameter("point");
		String level = request.getParameter("level");
		System.out.println("/fleet-info?map=" + map + "&point=" + point + "&level=" + level);

		// クエリを実行する(指定した条件の敵艦一覧を取り出す)
		List<Map<String, Object>> result;
		if (map == null || point == null || level == null) {
			result = new ArrayList<>();
		}else {
			int finalFlg = point.contains(" (Final)") ? 1 : 0;
			point = point.replace(" (Final)", "");
			String query = "SELECT fc.category AS formation, CASE WHEN unit_index < 6 THEN 1 ELSE 2 END AS index1,\r\n" + 
					"CASE WHEN unit_index < 6 THEN unit_index + 1 ELSE unit_index - 5 END AS index2,\r\n" + 
					"kammusu.name, slotsize, slot1, slot2, slot3, slot4, slot5,\r\n" + 
					"w1.name AS weapon1, w2.name AS weapon2, w3.name AS weapon3,\r\n" + 
					"w4.name AS weapon4, w5.name AS weapon5\r\n" + 
					"FROM position,weapon AS w1,weapon AS w2,weapon AS w3,weapon AS w4,weapon AS w5\r\n" + 
					",formation_category AS fc\r\n" +
					"INNER JOIN kammusu ON kammusu.id = position.enemy\r\n" + 
					"WHERE map=? AND position.name=? AND final_flg=?\r\n" + 
					"AND w1.id = kammusu.weapon1 AND w2.id = kammusu.weapon2\r\n" + 
					"AND w3.id = kammusu.weapon3 AND w4.id = kammusu.weapon4\r\n" + 
					"AND w5.id = kammusu.weapon5 AND fc.id=position.formation\r\n" + 
					"ORDER BY unit_index";
			result = database.select(query, map, point, finalFlg);
		}
		
		// クエリを実行する(それぞれの敵艦の情報を取り出し文字列化する)
		StringBuffer buffer = new StringBuffer();
		boolean add_formation_flg = false;
		for(Map<String, Object> pair : result) {
			// 陣形
			if (!add_formation_flg) {
				String formation = (String) pair.get("formation");
				buffer.append(String.format("%s%n", formation));
				add_formation_flg = true;
			}

			// 艦隊番号
			int index1 = (Integer) pair.get("index1");
			int index2 = (Integer) pair.get("index2");
			String unitIndexString = index1 == 1 ? "" + index2 : "" + index1 + "-" + index2;
			buffer.append(String.format("(%s)", unitIndexString));
			
			// 艦名
			String name = (String) pair.get("name");
			buffer.append(name);
			
			// スロット数
			int slotSize = (Integer)pair.get("slotsize");
			
			// 装備情報
			List<String> temp = new ArrayList<>();
			for(int i = 1; i <= slotSize; ++i) {
				int slot = (Integer)pair.get("slot" + i);
				String weaponName = (String)pair.get("weapon" + i);
				temp.add(String.format("[%d]%s", slot, weaponName));
			}
			buffer.append(String.format("　%s%n", String.join(",", temp)));
		}
		
		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(buffer.toString()));
	}
}

