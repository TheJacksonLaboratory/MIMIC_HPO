package org.jax.io;

import org.apache.commons.lang3.StringUtils;
import org.jax.Entity.JHULab;
import org.jax.Entity.LabEvent;
import org.jax.jdbc.ResultSetUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Date;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;

public class JHULabViewFactory {

    private static final Logger logger = LoggerFactory.getLogger(JHULabViewFactory.class);

	public static JHULab parse(ResultSet rs) throws SQLException {
		String lab_result_id = rs.getString("LAB_RESULT_CM_ID");
		String subject_id = rs.getString("PATID");
		String hadm_id = rs.getString("ENCOUNTERID");
		String loinc = rs.getString("LAB_LOINC");
		Date result_date = rs.getDate("RESULT_DATE");
        Float valuenum = Float.parseFloat(rs.getString("RESULT_NUM").trim());
        String valueuom = ResultSetUtil.getStringOrBlank(rs, "LOINC_UNIT").trim().replace("\"", "");
        String low = rs.getString("RANGE_LOW").trim();
        String high = rs.getString("RANGE_HIGH").trim();
        
		JHULab lab = new JHULab(lab_result_id, 
				subject_id, 
				hadm_id, 
				loinc, 
				result_date, 
				"", 
				valuenum, 
				"", 
				"", 
				valueuom, 
				low, 
				high);
		
		return lab;
	
	}

}
