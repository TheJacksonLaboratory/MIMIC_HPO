package org.jax.jdbc;

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

	private final String labSummaryStatistics = "select a.itemid, valueuom, i.loinc_code as 'loinc', counts, mean_all, min_normal, mean_normal, max_normal from\n" + 
			"(select e.itemid, e.valueuom, count(*) as counts, avg(valuenum) as mean_all,\n" + 
			"min(case when (valuenum IS NOT NULL and (flag IS NULL OR UPPER(flag)!='ABNORMAL')) then valuenum else null end) as min_normal,\n" + 
			"avg(case when (valuenum IS NOT NULL and (flag IS NULL OR UPPER(flag)!='ABNORMAL')) then valuenum else null end) as mean_normal,\n" + 
			"max(case when (valuenum IS NOT NULL and (flag IS NULL OR UPPER(flag)!='ABNORMAL')) then valuenum else null end) as max_normal\n" + 
			"from labevents e\n" + 
			"GROUP BY e.itemid, e.valueuom) as a\n" + 
			"join d_labitems i on a.itemid = i.itemid";
	
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
				statistics.setMean_all(ResultSetUtil.getDoubleOrNull(rs, "mean_all"));
				statistics.setMin_normal(ResultSetUtil.getDoubleOrNull(rs, "min_normal"));
				statistics.setMean_normal(ResultSetUtil.getDoubleOrNull(rs, "mean_normal"));
				statistics.setMax_normal(ResultSetUtil.getDoubleOrNull(rs, "max_normal"));
				return statistics;
			}  
		};
		
	}

}
