package jp.ysrken.kacs.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import jp.ysrken.kacs.SearcherService;
import jp.ysrken.kacs.model.FleetData;
import jp.ysrken.kacs.model.KammusuType;
import jp.ysrken.kacs.model.WeaponData;
import jp.ysrken.kacs.model.WeaponType;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

@SuppressWarnings("serial")
@WebServlet(name = "FinalAttack", urlPatterns = { "/final-attack" })
public class FinalAttack extends HttpServlet {
    /**
     * 基本攻撃力を出す
     * @param fleet 艦
     * @param type 攻撃種
     * @return 基本攻撃力
     */
    private double calcBasicAttack(FleetData fleet, String type) {
        double sum = 0.0;
        if (type.equals("航空")) {
            for (int i = 0; i < fleet.getWeapon().size(); ++i) {
                WeaponData weapon = fleet.getWeapon().get(i);
                int slotSize = fleet.getSlotCount().get(i);
                if (slotSize <= 0) {
                    continue;
                }
                if (weapon.getType() == WeaponType.CarrierAttacker.ordinal()) {
                    sum += (weapon.getTorpedo() * Math.sqrt(slotSize) + 25) * 1.5;
                }
                if (weapon.getType() == WeaponType.CarrierBomber.ordinal()
                    || weapon.getType() == WeaponType.FighterBomber.ordinal()
                    || weapon.getType() == WeaponType.SeaBomber.ordinal()) {
                    // sum += (weapon.getBomber() * Math.sqrt(slotSize) + 25);  // 実装漏れ
                }
            }
        } else if (type.equals("砲撃")) {
            if (fleet.getType() == KammusuType.CV.ordinal()
             || fleet.getType() == KammusuType.ACV.ordinal()
             || fleet.getType() == KammusuType.CVL.ordinal()) {
                // 空母砲撃戦
                double temp = fleet.getAttack() + fleet.getTorpedo();
                for (int i = 0; i < fleet.getWeapon().size(); ++i) {
                    WeaponData weapon = fleet.getWeapon().get(i);
                    if (weapon.getType() == WeaponType.CarrierAttacker.ordinal()
                        || weapon.getType() == WeaponType.CarrierBomber.ordinal()
                        || weapon.getType() == WeaponType.FighterBomber.ordinal()
                        || weapon.getType() == WeaponType.SeaBomber.ordinal()) {
                        temp += weapon.getTorpedo();
                        // temp += Math.floor(weapon.getBomber() * 1.3);  // 実装漏れ
                    }
                }
                sum = Math.floor(temp * 1.5) + 55;
            } else {
                // 通常砲撃戦
                sum += fleet.getAttack() + 5;
                for (int i = 0; i < fleet.getWeapon().size(); ++i) {
                    WeaponData weapon = fleet.getWeapon().get(i);
                    sum += weapon.getAttack();
                }
            }
        } else if (type.equals("対潜")) {
            // sum += Math.sqrt(fleet.getAntiSub()) * 2;  // 実装漏れ
            if (fleet.getType() == KammusuType.CVL.ordinal()) {
                // 航空対潜
                sum += 8.0;
            } else {
                // 通常対潜
                sum += 13.0;
            }
            for (int i = 0; i < fleet.getWeapon().size(); ++i) {
                WeaponData weapon = fleet.getWeapon().get(i);
                // sum += weapon.getAntiSub() * 1.5;  // 実装漏れ
            }
        } else if (type.equals("雷撃")) {
            // 通常砲撃戦
            sum += fleet.getTorpedo() + 5;
            for (int i = 0; i < fleet.getWeapon().size(); ++i) {
                WeaponData weapon = fleet.getWeapon().get(i);
                sum += weapon.getTorpedo();
            }
        } else if (type.equals("夜戦")) {
            for (int i = 0; i < fleet.getWeapon().size(); ++i) {
                WeaponData weapon = fleet.getWeapon().get(i);
                sum += weapon.getAttack();
                sum += weapon.getTorpedo();
            }
        }
        return sum;
    }

    /**
     * キャップ前攻撃力を出す
     * @param basicAttack 基本攻撃力
     * @param formation 陣形
     * @param status 交戦形態
     * @return キャップ前攻撃力
     */
    private double calcBeforeCapAttack(double basicAttack, String formation, String status, String type) {
        final Map<String, Double> statusDict = new HashMap<String, Double>(){{
            put("T有", 1.2);
            put("同航", 1.0);
            put("反航", 0.8);
            put("T不", 0.6);
        }};
        double statusParam = 1.0;
        final Map<String, Double> formationDict1 = new HashMap<String, Double>(){{
            put("単縦", 1.0);
            put("複縦", 0.8);
            put("輪形", 0.7);
            put("梯形", 0.6);
            put("単横", 0.6);
            put("第一(単横)", 0.6);
            put("第二(複縦)", 0.8);
            put("第三(輪形)", 0.7);
            put("第四(単縦)", 1.0);
        }};
        final Map<String, Double> formationDict2 = new HashMap<String, Double>(){{
            put("単縦", 0.6);
            put("複縦", 0.8);
            put("輪形", 1.2);
            put("梯形", 1.0);
            put("単横", 1.3);
            put("第一(単横)", 1.3);
            put("第二(複縦)", 0.8);
            put("第三(輪形)", 1.2);
            put("第四(単縦)", 0.6);
        }};
        if (type.equals("砲撃") || type.equals("雷撃")) {
            statusParam = formationDict1.get(formation);
        }
        if (type.equals("対潜")) {
            statusParam = formationDict2.get(formation);
        }
        // 負傷時の補正はめんどいので省いた
        return basicAttack * statusDict.get(status) * statusParam;
    }

    /**
     * キャップ後攻撃力を出す
     * @param beforeCapAttack キャップ前攻撃力
     * @param type 攻撃種
     * @return キャップ後攻撃力
     */
    private double calcAfterCapAttack(double beforeCapAttack, String type) {
        double limit = 180.0;
        if (type.equals("対潜")) {
            limit = 100.0;
        } else if (type.equals("夜戦")) {
            limit = 300.0;
        }
        return (limit > beforeCapAttack ? beforeCapAttack : limit + Math.sqrt(beforeCapAttack - limit));
    }

    /**
     * 最終攻撃力を出す
     * @param afterCapAttack キャップ後攻撃力
     * @return 最終攻撃力
     */
    private double calcFinalAttack(double afterCapAttack) {
        return Math.floor(afterCapAttack);
    }

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
        String name = request.getParameter("name");
        String formation = request.getParameter("formation");
        String status = request.getParameter("status");
        String type = request.getParameter("type");
        System.out.println("/final-attack?map=" + map + "&point=" + point + "&name=" + name + "&formation=" + formation + "&status=" + status + "&type=" + type);

        // クエリを実行する(指定した条件の敵艦一覧を取り出す)
        Map<String, Object> res = new LinkedHashMap<>();
        FleetData enemyFleet = searcher.findFromMapAndPointAndName(map, point, name);

        // 最終攻撃力を計算する
        double basicAttack = calcBasicAttack(enemyFleet, type); // 基礎攻撃力
        double beforeCapAttack = calcBeforeCapAttack(basicAttack, formation, status, type);   // キャップ前攻撃力
        double afterCapAttack = calcAfterCapAttack(beforeCapAttack, type);  // キャップ後攻撃力
        double finalAttack = calcFinalAttack(afterCapAttack);    //最終攻撃力
        res.put("value", (int)finalAttack);

        // 結果をJSONで返却する
        response.setContentType("text/json");
        response.setCharacterEncoding("UTF-8");
        response.setHeader("Access-Control-Allow-Origin", "*");
        ObjectMapper mapper = new ObjectMapper();
        response.getWriter().println(mapper.writeValueAsString(res));
    }
}
