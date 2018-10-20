package jp.ysrken.kacs;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

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
	 * value・name形式の結果を返す
	 * 
	 * @param query
	 *            SQLクエリ
	 * @param valueKey
	 *            valueに入れる値
	 * @param nameKey
	 *            nameに入れる値
	 * @return
	 */
	public List<ValueNamePair> findValueNamePair(String query, String valueKey, String nameKey) {
		List<ValueNamePair> result = new ArrayList<>();
		try {
			// クエリを実行するための準備をする
			Statement statement = connection.createStatement();
			statement.setQueryTimeout(30);

			// SELECT文を発行する
			ResultSet rs = statement.executeQuery(query);
			while (rs.next()) {
				ValueNamePair pair = new ValueNamePair() {
					{
						setValue(rs.getString(valueKey));
						setName(rs.getString(nameKey));
					}
				};
				result.add(pair);
			}
			return result;
		} catch (SQLException e) {
			e.printStackTrace();
			return result;
		}
	}
}
