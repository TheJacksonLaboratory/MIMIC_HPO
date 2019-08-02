package org.jax.io;

import org.apache.commons.lang3.StringUtils;
import org.jax.Entity.LabEvent;
import org.jax.jdbc.ResultSetUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.Date;

public class JHULabViewFactory {

    private static final Logger logger = LoggerFactory.getLogger(JHULabViewFactory.class);

	public static JHULab parse(ResultSet rs) throws SQLException {
		int subject_id = rs.getInt("PATID");
		int hadm_id = rs.getInt("ENCOUNTERID");
		Date result_date = rs.getDate("RESULT_DATE");
        Double valuenum = Double.parseDouble(rs.getString("RESULT_NUM").trim());
        String valueuom = ResultSetUtil.getStringOrBlank(rs, "LOINC_UNIT").trim().replace("\"", "");
        Double range_low = Double.parseDouble(rs.getString("RANGE_LOW").trim());
        Double range_high = Double.parseDouble(rs.getString("RANGE_HIGH").trim());
        
		JHULab lab = new JHULab(
                subject_id,
                hadm_id,
                result_date,
                valuenum,
                valueuom,
                range_low,
                range_high);
		
		return lab;
	
	}

}
