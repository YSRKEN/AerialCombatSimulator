package jp.ysrken.kacs.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import jp.ysrken.kacs.SearcherService;
import jp.ysrken.kacs.model.OwnData;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collector;
import java.util.stream.Collectors;

@SuppressWarnings("serial")
@WebServlet(name = "FleetInfo", urlPatterns = { "/enemy-names" })
public class EnemyNames extends HttpServlet {
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
            OwnData enemyFleets = searcher.findFromEnemyData(map, point);
            res.put("enemy", enemyFleets.getFleet().stream().map(fleet -> {
                Map<String, Object> fleetInfo = new HashMap<>();
                fleetInfo.put("id", Integer.parseInt(fleet.getId()));
                fleetInfo.put("name", fleet.getName());
                return fleetInfo;
            }).collect(Collectors.toList()));
        }

        // 結果をJSONで返却する
        response.setContentType("text/json");
        response.setCharacterEncoding("UTF-8");
        response.setHeader("Access-Control-Allow-Origin", "*");
        ObjectMapper mapper = new ObjectMapper();
        response.getWriter().println(mapper.writeValueAsString(res));
    }
}
