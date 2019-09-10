package org.jax.text2hpo;

import org.jax.Entity.NoteEvent;
import org.jax.Entity.NoteHpo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;
import org.springframework.stereotype.Component;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;

/**
 * This class converts radiology of NoteEvents in MIMIC into HPO terms.
 * Note: it can be refactored to deal with all texts in NoteEvents by changing:
 * 1. SQL query. Return other documents of interest
 * 2. preprocessing in the NoteEventCallbackHandler inner class.
 */
@Component
public class MimicRadiology2Hpo {

    final static Logger logger = LoggerFactory.getLogger(MimicRadiology2Hpo.class);

    @Autowired
    JdbcTemplate jdbcTemplate;
    @Autowired
    TransactionTemplate transactionTemplate;
    @Autowired
    UmlsText2HpoService umlsText2HpoService;

    List<NoteHpo> noteHpos = new ArrayList<>();

    public void initTable(){
        String query = "CREATE TABLE IF NOT EXISTS NoteHpo(ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NOTES_ROW_ID INT, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
        jdbcTemplate.execute("TRUNCATE NoteHpo;");
    }

    public void note2hpo(int batch_size){

        //initTable();
        //min is 738405, max 1260683; all records within this range are for radiology
        final String row_id_min_query = "SELECT min(row_id) FROM NOTEEVENTS WHERE CATEGORY = 'Radiology'";
        final String row_id_max_query = "SELECT max(row_id) FROM NOTEEVENTS WHERE CATEGORY = 'Radiology'";
        final String batch_notes = "SELECT * FROM NOTEEVENTS WHERE CATEGORY = 'Radiology' AND ROW_ID BETWEEN ? and ?";
        Integer row_id_min = jdbcTemplate.queryForObject(row_id_min_query, Integer.class);
        Integer row_id_max = jdbcTemplate.queryForObject(row_id_max_query, Integer.class);
//manually control
        row_id_min = 738405;
        row_id_max = 739000;
        int total_rows = row_id_max - row_id_min;
        final int BATCH_N = total_rows / batch_size + 1;
        for (int i = 0; i < BATCH_N; i++){
            jdbcTemplate.query(batch_notes, new Object[]{i * batch_size + row_id_min,
                    i * batch_size + row_id_min + batch_size - 1},
                    new NoteEventCallbackHandler(umlsText2HpoService));
        }
        if (!noteHpos.isEmpty()){
            insertBatch(noteHpos);
            noteHpos.clear();
        }

    }

    private class NoteEventCallbackHandler implements RowCallbackHandler {

        private UmlsText2HpoService umlsText2HpoService;

        NoteEventCallbackHandler(UmlsText2HpoService umlsText2HpoService) {
            this.umlsText2HpoService = umlsText2HpoService;
        }

        @Override
        public void processRow(ResultSet rs) throws SQLException {

            NoteEvent noteEvent = NoteEventFactory.parse(rs);
            int note_rowId = noteEvent.getRow_id();
            String note_text = noteEvent.getText();
            //TODO: use a case-switch statement to handle preprocessing according to document type
            Optional<String> final_report_section = NoteEventFactory.get_radiology_final_report(note_text);
            final_report_section.ifPresent(report -> {
                String preprocessed = final_report_section.get().trim().replace("\n", " ");
                Set<UmlsText2HpoService.PositionUnawareTextMinedTerm> minedTermSet = umlsText2HpoService.minedTerms(preprocessed);

                logger.info(String.format("UMLS miner found %d terms", minedTermSet.size()));
                for (UmlsText2HpoService.PositionUnawareTextMinedTerm minedTerm : minedTermSet){
                    String negated = minedTerm.isPresent()? "F" : "T";
                    NoteHpo newNoteHpo = new NoteHpo(note_rowId, negated, minedTerm.getTermid());
                    noteHpos.add(newNoteHpo);
                }
            });

            if (noteHpos.size() >= 100) {
                insertBatch(noteHpos);
                noteHpos.clear();
            }


        }

    }

    public void insertBatch(final List<NoteHpo> noteHpos) {

//        String sql = "INSERT INTO NoteHpo " + "(NOTES_ROW_ID, NEGATED, MAP_TO) VALUES (?, ?, ?)";
//
//        transactionTemplate.execute(new TransactionCallbackWithoutResult() {
//
//            @Override
//            protected void doInTransactionWithoutResult(TransactionStatus status) {
//                jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
//
//                    @Override
//                    public void setValues(PreparedStatement ps, int i) throws SQLException {
//                        NoteHpo noteHpo = noteHpos.get(i);
//                        ps.setInt(1, noteHpo.getRowid_note());
//                        ps.setString(2, noteHpo.getNegated());
//                        ps.setString(3, noteHpo.getMapTo());
//                    }
//
//                    @Override
//                    public int getBatchSize() {
//                        return noteHpos.size();
//                    }
//                });
//            }
//        });
        noteHpos.forEach(System.out::println);
    }



}
