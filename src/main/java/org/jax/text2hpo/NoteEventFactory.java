package org.jax.text2hpo;

import org.jax.Entity.NoteEvent;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.Optional;

public class NoteEventFactory {

    public static NoteEvent parse(ResultSet rs) throws SQLException {
        int row_id = rs.getInt("ROW_ID");
        int subject_id = rs.getInt("SUBJECT_ID");
        int hadm_id = rs.getInt("HADM_ID");
        Timestamp chartdate = rs.getTimestamp("CHARTDATE");
        Timestamp charttime = rs.getTimestamp("CHARTTIME");
        Timestamp storetime = rs.getTimestamp("STORETIME");
        String category = rs.getString("CATEGORY");
        String description = rs.getString("DESCRIPTION");
        int cgid = rs.getInt("CGID");
        String iserror = rs.getString("ISERROR");
        String text = rs.getString("TEXT");



        NoteEvent noteEvent = new NoteEvent(row_id,
                subject_id,
                hadm_id,
                chartdate,
                charttime,
                storetime,
                category,
                description,
                cgid,
                iserror,
                text);

        return noteEvent;
    }

    /**
     * Preprocess the radiology reports. Extract the FINAL REPORT section
     * @param text content in the database
     * @return the final report section of radiology reports
     */
    public static Optional<String> get_radiology_final_report(String text){
        if (text.toLowerCase().trim().equals("null")){
            return Optional.empty();
        }
        final String SECTION_SEP = "______________________________________________________________________________";
        String[] sections = text.split(SECTION_SEP);
        for (String section : sections){
            if (section.contains("FINAL REPORT")){
                return Optional.of(section);
            }
        }
        return Optional.empty();
    }


}
