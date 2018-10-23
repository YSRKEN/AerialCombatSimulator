package jp.ysrken.kacs;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.ServletContext;

import lombok.Getter;

public class DatabaseService {
	/**
	 * 自分自身の唯一のインスタンス
	 */
	@Getter
	private static DatabaseService database = null;
	
	/**
	 * コネクション情報
	 */
	private Connection connection = null;

	/**
	 * privateコンストラクタ
	 */
	private DatabaseService() {
	}

	/**
	 * データベースを初期化する
	 * 
	 * @param fileName
	 */
	public static void initialize(ServletContext servletContext) {
		if (database != null) {
			return;
		}
		try {
			database = new DatabaseService();
			String databasePath = servletContext.getRealPath("WEB-INF/GameData.db");
			database.connection = DriverManager.getConnection("jdbc:sqlite:" + databasePath);
		} catch (SQLException e) {
			e.printStackTrace();
			database = null;
		}
	}

	/**
	 * SELECTの結果を返す
	 * 
	 * @param query
	 *            SQLクエリ
	 * @return SELECTした結果をMapのListで返す
	 */
	public List<Map<String, Object>> select(String query) {
		List<Map<String, Object>> result = new ArrayList<>();
		try {
			// クエリを実行するための準備をする
			Statement statement = connection.createStatement();
			statement.setQueryTimeout(30);

			// SELECT文を発行する
			ResultSet rs = statement.executeQuery(query);
			ResultSetMetaData rsmd = rs.getMetaData();
			int columnCount = rsmd.getColumnCount();
			while (rs.next()) {
				Map<String, Object> record = new HashMap<>();
				for (int i = 1; i <= columnCount; ++i) {
					String key = rsmd.getColumnLabel(i);
					Object value = rs.getObject(i);
					record.put(key, value);
				}
				result.add(record);
			}
			return result;
		} catch (SQLException e) {
			e.printStackTrace();
			return result;
		}
	}
}
