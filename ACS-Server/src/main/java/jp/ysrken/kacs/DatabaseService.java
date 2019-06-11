package jp.ysrken.kacs;

import lombok.Getter;

import javax.servlet.ServletContext;
import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
	 * クエリの実行結果を返す
	 * 
	 * @param query SQLクエリ
	 * @return ResultSetを返す
	 * @throws SQLException
	 */
	public ResultSet getResultSet(String query) throws SQLException {
		// クエリを実行するための準備をする
		Statement statement = connection.createStatement();
		statement.setQueryTimeout(30);
		
		// SELECT文を発行する
		return statement.executeQuery(query);
	}
	
	/**
	 * クエリの実行結果を返す
	 * 
	 * @param query SQLクエリ
	 * @param param1 パラメーター1
	 * @return ResultSetを返す
	 * @throws SQLException
	 */
	public <T> ResultSet getResultSet(String query, T param1) throws SQLException {
		// クエリを実行するための準備をする
		PreparedStatement preparedStatement = connection.prepareStatement(query);
		preparedStatement.setQueryTimeout(30);
		
		if (param1.getClass() == String.class) {
			preparedStatement.setString(1, (String) param1);
		}else {
			preparedStatement.setObject(1, param1);
		}
		
		// SELECT文を発行する
		return preparedStatement.executeQuery();
	}

	/**
	 * クエリの実行結果を返す
	 * 
	 * @param query SQLクエリ
	 * @param param1 パラメーター1
	 * @param param2 パラメーター2
	 * @param param3 パラメーター3
	 * @return ResultSetを返す
	 * @throws SQLException
	 */
	public <T,U,V> ResultSet getResultSet(String query, T param1, U param2, V param3) throws SQLException {
		// クエリを実行するための準備をする
		PreparedStatement preparedStatement = connection.prepareStatement(query);
		preparedStatement.setQueryTimeout(30);
		
		if (param1.getClass() == String.class) {
			preparedStatement.setString(1, (String) param1);
		}else {
			preparedStatement.setObject(1, param1);
		}
		
		if (param2.getClass() == String.class) {
			preparedStatement.setString(2, (String) param2);
		}else {
			preparedStatement.setObject(2, param2);
		}
		
		if (param3.getClass() == String.class) {
			preparedStatement.setString(3, (String) param3);
		}else {
			preparedStatement.setObject(3, param3);
		}
		
		// SELECT文を発行する
		return preparedStatement.executeQuery();
	}
	
	/**
	 * 実行結果をMapのListに変換する
	 * 
	 * @param rs 実行結果
	 * @return MapのList
	 * @throws SQLException
	 */
	public List<Map<String, Object>> getResult(ResultSet rs) throws SQLException {
		List<Map<String, Object>> result = new ArrayList<>();
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
	}
	
	/**
	 * SELECTの結果を返す
	 * 
	 * @param query SQLクエリ
	 * @return SELECTした結果をMapのListで返す
	 */
	public List<Map<String, Object>> select(String query) {
		try {
			// クエリから結果を取得する
			ResultSet rs = getResultSet(query);
			
			// 結果をMapのListに変換する
			return getResult(rs);
		} catch (SQLException e) {
			e.printStackTrace();
			return new ArrayList<>();
		}
	}

	/**
	 * SELECTの結果を返す
	 * 
	 * @param query SQLクエリ
	 * @param param1 パラメーター1
	 * @return SELECTした結果をMapのListで返す
	 */
	public <T> List<Map<String, Object>> select(String query, T param1) {
		try {
			// クエリから結果を取得する
			ResultSet rs = getResultSet(query, param1);
			
			// 結果をMapのListに変換する
			return getResult(rs);
		} catch (SQLException e) {
			e.printStackTrace();
			return new ArrayList<>();
		}
	}
	
	/**
	 * SELECTの結果を返す
	 * 
	 * @param query SQLクエリ
	 * @param param1 パラメーター1
	 * @param param1 パラメーター2
	 * @param param1 パラメーター3
	 * @return SELECTした結果をMapのListで返す
	 */
	public <T,U,V> List<Map<String, Object>> select(String query, T param1, U param2, V param3) {
		try {
			// クエリから結果を取得する
			ResultSet rs = getResultSet(query, param1, param2, param3);
			
			// 結果をMapのListに変換する
			return getResult(rs);
		} catch (SQLException e) {
			e.printStackTrace();
			return new ArrayList<>();
		}
	}
}
