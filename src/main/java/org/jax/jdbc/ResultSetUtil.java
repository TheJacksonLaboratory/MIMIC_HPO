package org.jax.jdbc;

import java.sql.ResultSet;
import java.sql.SQLException;

public class ResultSetUtil {

	// Override the resultSet behavior of returning 0.0 if the field is null
	public static Double getDoubleOrNull(ResultSet rs, String fieldName) throws SQLException {
		Double result = rs.getDouble(fieldName);
		if (rs.wasNull()) {
			result = null;
		}
		return result;
	}
	
	// Override the resultSet behavior of returning null if the field is null, returning an empty string instead
	public static String getStringOrBlank(ResultSet rs, String fieldName) throws SQLException {
		String result = rs.getString(fieldName);
		if (result == null) {
			result = "";
		}
		return result;
	}


}
