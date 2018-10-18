package jp.ysrken.kacs;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

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

		// SQLite用のJDBCドライバを使用する
		try {
			Class.forName("org.sqlite.JDBC");
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
			return;
		}

		// クエリを実行する
		String databasePath = getServletContext().getRealPath("WEB-INF/GameData.db");
		try (Connection connection = DriverManager.getConnection("jdbc:sqlite:" + databasePath)) {
			// クエリを実行するための準備をする
			Statement statement = connection.createStatement();
			statement.setQueryTimeout(30);

			// SELECT文を発行する
			ResultSet rs = statement.executeQuery("SELECT id, name FROM weapon_type ORDER BY id");
			List<ValueNamePair> result = new ArrayList<>();
			while (rs.next()) {
				ValueNamePair pair = new ValueNamePair(){{
					setValue(Integer.toString(rs.getInt("id")));
					setName(rs.getString("name"));
				}};
				result.add(pair);
			}
			
			// 結果をJSONで返却する
			response.setContentType("text/json");
			response.setCharacterEncoding("UTF-8");
			ObjectMapper mapper = new ObjectMapper();
			response.getWriter().println(mapper.writeValueAsString(result));
		} catch (SQLException e) {
			e.printStackTrace();
			response.sendError(500);
			return;
		}
	}
}

@Data
@AllArgsConstructor
@NoArgsConstructor
class ValueNamePair {
	private String value;
	private String name;
}
