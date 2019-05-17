package org.jax.io;

import org.jax.Entity.LabEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.awt.geom.FlatteningPathIterator;
import java.sql.Timestamp;

public class LabEventFactory {

    private static final Logger logger = LoggerFactory.getLogger(LabEventFactory.class);

    public static LabEvents parse(String record) throws MimicHpoException {

        if (record.endsWith(",")) {
            record = record + " ";
        }

        String[] elements = record.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");
        if (elements.length != 9) {
            logger.warn("The record does not have 9 fields");
            //throw new RuntimeException();
        }

        LabEvents event = null;

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
            String value = elements[5];
            float valuenum;
            if (elements[6].isEmpty()) {
                valuenum = Float.MAX_VALUE;
            } else {
                valuenum = Float.parseFloat(elements[6].trim());
            }
            String valueuom = elements[7];
            String flag = elements[8];

            event = new LabEvents(row_id,
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

}
