package jp.ysrken.kacs.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import jp.ysrken.kacs.SearcherService;
import jp.ysrken.kacs.model.LbasData;
import jp.ysrken.kacs.model.OwnData;
import jp.ysrken.kacs.model.SimulationData;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;

@SuppressWarnings("serial")
@WebServlet(name = "LbasInfo", urlPatterns = { "/lbas-info" })
public class LbasInfo extends HttpServlet {
    @Override
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        // データベースを確認する
        SearcherService.initialize(getServletContext());
        if (SearcherService.getInstance() == null) {
            response.sendError(500);
            return;
        }

        // POSTされたデータを確認する
        //基地航空隊・敵艦隊・自艦隊の情報
        BufferedReader reader = request.getReader();

        // リクエストボディからJSON部分を取り出し、オブジェクトに変更
        ObjectMapper mapper = new ObjectMapper();
        LbasData lbasData =
                mapper.readValue(reader, LbasData.class);

        // 計算結果を返す
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("AntiAirValue", lbasData.calcAntiAirValue());
        result.put("Radius", lbasData.calcRadius());

        // 結果をJSONで返却する
        response.setContentType("text/json");
        response.setCharacterEncoding("UTF-8");
        response.setHeader("Access-Control-Allow-Origin", "*");
        response.getWriter().println(mapper.writeValueAsString(result));
    }
}
