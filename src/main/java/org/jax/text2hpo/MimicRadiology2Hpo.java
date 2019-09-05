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
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;

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
    private PlatformTransactionManager transactionManager;
    @Autowired
    UmlsText2HpoService umlsText2HpoService;
    //the field will be updated to record the total number of rows to process. It will be used in the inner class to detect the end of processing rows
    Integer TOTAL_ROWS_TO_PROCESS = 0;
    //the filed will be used to track how many rows have been processed
    int processed_rows_counter = 0;

    String ROW_COUNT = "SELECT count(*) FROM NOTEEVENTS WHERE CATEGORY = 'Radiology'";
    String allNotes = "SELECT * FROM NOTEEVENTS WHERE CATEGORY = 'Radiology'";

    public void initTable(){
        String query = "CREATE TABLE IF NOT EXISTS NoteHpo(ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NOTES_ROW_ID INT, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
        jdbcTemplate.execute("TRUNCATE NoteHpo;");
    }

    public void note2hpo(){

        // The fetch size will limit how many results come back at once reducing memory
        // requirements. This is the specific recommendation for MySQL and may need to
        // be varied for other dbs
        jdbcTemplate.setFetchSize(Integer.MIN_VALUE);
        initTable();
        this.TOTAL_ROWS_TO_PROCESS = jdbcTemplate.queryForObject(ROW_COUNT, null, Integer.class);
        jdbcTemplate.query(allNotes,
                new NoteEventCallbackHandler(jdbcTemplate, transactionManager, umlsText2HpoService));

    }

    private class NoteEventCallbackHandler implements RowCallbackHandler {

        int batchSize = 20000;
        JdbcTemplate jdbcTemplate;
        TransactionTemplate transactionTemplate;
        UmlsText2HpoService umlsText2HpoService;
        List<NoteHpo> noteHpos = new ArrayList<>(batchSize);

        NoteEventCallbackHandler(JdbcTemplate jdbcTemplate, PlatformTransactionManager transactionManager,
                                UmlsText2HpoService umlsText2HpoService) {
            this.jdbcTemplate = jdbcTemplate;
            this.transactionTemplate = new TransactionTemplate(transactionManager);
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

            //update processed row counter by one
            processed_rows_counter += 1;

            if (noteHpos.size() >= batchSize || processed_rows_counter == TOTAL_ROWS_TO_PROCESS) {
                insertBatch(noteHpos);
                noteHpos.clear();
            }

        }

        public void insertBatch(final List<NoteHpo> noteHpos) {

            String sql = "INSERT INTO NoteHpo " + "(NOTES_ROW_ID, NEGATED, MAP_TO) VALUES (?, ?, ?)";

            transactionTemplate.execute(new TransactionCallbackWithoutResult() {

                @Override
                protected void doInTransactionWithoutResult(TransactionStatus status) {
                    jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {

                        @Override
                        public void setValues(PreparedStatement ps, int i) throws SQLException {
                            NoteHpo noteHpo = noteHpos.get(i);
                            ps.setInt(1, noteHpo.getRowid_note());
                            ps.setString(2, noteHpo.getNegated());
                            ps.setString(3, noteHpo.getMapTo());
                        }

                        @Override
                        public int getBatchSize() {
                            return noteHpos.size();
                        }
                    });
                }
            });
        }

    }



}
