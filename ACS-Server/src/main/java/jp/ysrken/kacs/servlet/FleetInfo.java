package jp.ysrken.kacs.servlet;

import java.io.IOException;
import java.util.ArrayList;
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
		StringBuffer buffer = new StringBuffer();
		if (map == null || point == null || level == null) {
		} else {
			OwnData enemyFleets = searcher.findFromEnemyData(map, point);
			
			// 陣形
			buffer.append(String.format("%s%n", enemyFleets.getFormation()));
			
			// 艦隊情報
			for (int index = 0; index < enemyFleets.getFleet().size(); ++index) {
				FleetData fleet = enemyFleets.getFleet().get(index);
				
				// 艦隊番号
				buffer.append(String.format("(%d)", index + 1));
				
				// 艦名
				buffer.append(fleet.getName());
				
				// 装備情報
				List<String> temp = new ArrayList<>();
				fleet.getWeapon().forEach(weapon -> {
					temp.add(String.format("[%d]%s", weapon.getSlotCount(), weapon.getName()));
				});
				buffer.append(String.format("　%s%n", String.join(",", temp)));
			}
		}

		// 結果をJSONで返却する
		response.setContentType("text/json");
		response.setCharacterEncoding("UTF-8");
		response.setHeader("Access-Control-Allow-Origin", "*");
		ObjectMapper mapper = new ObjectMapper();
		response.getWriter().println(mapper.writeValueAsString(buffer.toString()));
	}
}

