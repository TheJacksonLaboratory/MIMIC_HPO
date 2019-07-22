package org.jax;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

import org.jax.lab2hpo.LabSummaryStatistics;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

@Service
public class LabSummaryService {

    @Autowired
    JdbcTemplate jdbcTemplate;

	private final String labSummaryStatistics = "select e.itemid, e.valueuom, i.loinc_code as loinc, count(*) as counts, avg(valuenum) as mean_all,\n" + 
			"min(case when (valuenum IS NOT NULL and (flag IS NULL OR UPPER(flag)!='ABNORMAL')) then valuenum else null end) as min_normal,\n" + 
			"avg(case when (valuenum IS NOT NULL and (flag IS NULL OR UPPER(flag)!='ABNORMAL')) then valuenum else null end) as mean_normal,\n" + 
			"max(case when (valuenum IS NOT NULL and (flag IS NULL OR UPPER(flag)!='ABNORMAL')) then valuenum else null end) as max_normal\n" + 
			"from labevents e\n" + 
			"join d_labitems i on i.itemid = e.itemid\n" + 
			"GROUP BY e.itemid, e.valueuom";
	
	public List<LabSummaryStatistics> labSummaryStatistics() {		
		return jdbcTemplate.query(labSummaryStatistics, getRowMapper());
	}
	
	private RowMapper<LabSummaryStatistics> getRowMapper() {
	
		return new RowMapper<LabSummaryStatistics>(){  
	    
			@Override  
			public LabSummaryStatistics mapRow(ResultSet rs, int rownumber) throws SQLException {  
				LabSummaryStatistics statistics = new LabSummaryStatistics();
				statistics.setItemId(rs.getInt("itemid"));
				statistics.setValueuom(rs.getString("valueuom"));
				statistics.setLoinc(rs.getString("loinc"));
				statistics.setCounts(rs.getInt("counts"));
				statistics.setMean_all(getDoubleOrNull(rs, "mean_all"));
				statistics.setMin_normal(getDoubleOrNull(rs, "min_normal"));
				statistics.setMean_normal(getDoubleOrNull(rs, "mean_normal"));
				statistics.setMax_normal(getDoubleOrNull(rs, "max_normal"));
				return statistics;
			}  
		};
		
	}

	// Override the resultSet behavior of returning 0.0 if the field is null
	private static Double getDoubleOrNull(ResultSet rs, String fieldName) throws SQLException {
		Double result = rs.getDouble(fieldName);
		if (rs.wasNull()) {
			result = null;
		}
		return result;
	}

}
