package org.jax.io;

import org.apache.commons.lang3.StringUtils;
import org.jax.Entity.LabEvent;
import org.jax.jdbc.ResultSetUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;

public class LabEventFactory {

    private static final Logger logger = LoggerFactory.getLogger(LabEventFactory.class);

    public static LabEvent parse(String record) throws MimicHpoException {

        if (record.endsWith(",")) {
            record = record + " ";
        }

        String[] elements = record.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");
        if (elements.length != 9) {
            logger.warn("The record does not have 9 fields");
            //throw new RuntimeException();
        }

        LabEvent event = null;

        try {
            int row_id = Integer.parseInt(elements[0]);
            int subject_id = Integer.parseInt(elements[1]);
            int hadm_id;
            if (elements[2].isEmpty()) {
                hadm_id = Integer.MAX_VALUE;
            } else {
                hadm_id = Integer.parseInt(elements[2].trim());
            }
            int item_id = Integer.parseInt(elements[3]);
            Timestamp charttime = Timestamp.valueOf(elements[4]);
            String value = elements[5].trim().replace("\"", "");
            Double valuenum;
            if (StringUtils.isBlank(elements[6])) {
                valuenum = null;
            } else {
                valuenum = Double.parseDouble(elements[6].trim());
            }
            String valueuom = elements[7].trim().replace("\"", "");
            String flag = elements[8].trim().replace("\"", "");

            event = new LabEvent(row_id,
                    subject_id,
                    hadm_id,
                    item_id,
                    charttime,
                    value,
                    valuenum,
                    valueuom,
                    flag);
        } catch (NumberFormatException e){
            throw new MimicHpoException("parsing error: not a valid lab record" + record);
        }

        return event;
    }

	public static LabEvent parse(ResultSet rs) throws SQLException {
		int row_id = rs.getInt("ROW_ID");
		int subject_id = rs.getInt("SUBJECT_ID");
		int hadm_id = rs.getInt("HADM_ID");
		int item_id = rs.getInt("ITEMID");
		Timestamp charttime = rs.getTimestamp("CHARTTIME");
		String value = ResultSetUtil.getStringOrBlank(rs, "VALUE").trim().replace("\"", "");
        Double valuenum;
        if (StringUtils.isBlank(rs.getString("VALUENUM"))) {
        	valuenum = null;
        } else {
            valuenum = Double.parseDouble(rs.getString("VALUENUM").trim());
        }
        String valueuom = ResultSetUtil.getStringOrBlank(rs, "VALUEUOM").trim().replace("\"", "");
        String flag = ResultSetUtil.getStringOrBlank(rs, "FLAG").trim().replace("\"", "");

		LabEvent labEvent = new LabEvent(row_id,
                subject_id,
                hadm_id,
                item_id,
                charttime,
                value,
                valuenum,
                valueuom,
                flag);
		
		return labEvent;
	
	}

}
