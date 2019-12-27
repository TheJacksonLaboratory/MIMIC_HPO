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
import org.jax.text2hpo.UmlsText2HpoService.PositionUnawareTextMinedTerm;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
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

    //We can send a batch to MetaMap for query. To do this, uncomment lines below.
    //But it does not improve speed. They can be removed.
    Map<Integer, String> notesbuffer = new LinkedHashMap<>();
    List<NoteHpo> noteHpos = new ArrayList<>();

    public void initTable(){
        String query = "CREATE TABLE IF NOT EXISTS NoteHpo(ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NOTES_ROW_ID INT, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
        jdbcTemplate.execute("TRUNCATE NoteHpo;");
    }

    public void note2hpo(int batch_size){

        initTable();
        //min is 738405, max 1260683; all records within this range are for radiology
        final String row_id_min_query = "SELECT min(row_id) FROM NOTEEVENTS WHERE CATEGORY = 'Radiology'";
        final String row_id_max_query = "SELECT max(row_id) FROM NOTEEVENTS WHERE CATEGORY = 'Radiology'";
        final String batch_notes = "SELECT * FROM NOTEEVENTS WHERE CATEGORY = 'Radiology' AND ROW_ID BETWEEN ? and ?";
        Integer row_id_min = jdbcTemplate.queryForObject(row_id_min_query, Integer.class);
        Integer row_id_max = jdbcTemplate.queryForObject(row_id_max_query, Integer.class);
//manually control
        row_id_min = 738405;
        row_id_max = 738425;
        int total_rows = row_id_max - row_id_min;
        final int BATCH_N = total_rows / batch_size + 1;
        for (int i = 0; i < BATCH_N; i++){
            jdbcTemplate.query(batch_notes, new Object[]{i * batch_size + row_id_min,
                    i * batch_size + row_id_min + batch_size - 1},
                    new NoteEventCallbackHandler(umlsText2HpoService));
        }
//        if (!notesbuffer.isEmpty()){
//            noteHpos.addAll(query(notesbuffer));
//            notesbuffer.clear();
//        }
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
//                notesbuffer.put(note_rowId, preprocessed);

                Collection<PositionUnawareTextMinedTerm> minedTermSet = umlsText2HpoService.minedTerms_single(preprocessed);

                logger.info(String.format("UMLS miner found %d terms", minedTermSet.size()));
                for (PositionUnawareTextMinedTerm minedTerm : minedTermSet){
                    String negated = minedTerm.isPresent()? "F" : "T";
                    NoteHpo newNoteHpo = new NoteHpo(note_rowId, negated, minedTerm.getTermid());
                    noteHpos.add(newNoteHpo);
                }

//                if (notesbuffer.size() == 1){
//                    Collection<NoteHpo> queryresult = query(notesbuffer);
//                    logger.info(String.format("UMLS miner found %d terms for batch of %d", queryresult.size(), notesbuffer.size()));
//                    noteHpos.addAll(queryresult);
//                    notesbuffer.clear();
//                }

            });

            if (noteHpos.size() >= 100) {
                insertBatch(noteHpos);
                noteHpos.clear();
            }


        }

    }

//    public Collection<NoteHpo> query(Map<Integer, String> queries){
//        List<Integer> notes_ids = new ArrayList<>(queries.keySet());
//        List<String> notes_texts = new ArrayList<>(queries.values());
//        List<Set<PositionUnawareTextMinedTerm>> results = umlsText2HpoService.minedTerms_batch(notes_texts);
//        if (notes_ids.size() != results.size()){
//            logger.error(String.format("notes id size: %d; results size: %d", notes_ids.size(), results.size()));
//        }
//
//        List<NoteHpo> final_result = new ArrayList<>();
//        for (int i = 0; i < notes_ids.size(); i++){
//            int note_rowId = notes_ids.get(i);
//            Collection<PositionUnawareTextMinedTerm> minedTermSet = results.get(i);
//            for (PositionUnawareTextMinedTerm minedTerm : minedTermSet){
//                String negated = minedTerm.isPresent()? "F" : "T";
//                NoteHpo newNoteHpo = new NoteHpo(note_rowId, negated, minedTerm.getTermid());
//                final_result.add(newNoteHpo);
//            }
//        }
//
//        return final_result;
//    }


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
//        noteHpos.forEach(System.out::println);
    }

    public void importClinPhenResult(String path){
        initTableForClinPhen();
        List<NoteHpo> noteHpoList = new ArrayList<>();
        try(BufferedReader reader = new BufferedReader(new FileReader(path))){
            String line = reader.readLine();
            while ((line = reader.readLine()) != null){
                String [] elements = line.split("\t");
                int note_row_id = Integer.valueOf(elements[0]);
                String hp_term_id = elements[1];
                //all terms are present
                String negated = "F";
                NoteHpo noteHpo = new NoteHpo(note_row_id, negated, hp_term_id);
                noteHpoList.add(noteHpo);
                if (noteHpoList.size() > 2000){
                    insertBatchClinPhen(noteHpoList);
                    noteHpoList.clear();
                }
            }
        } catch (FileNotFoundException e){

        } catch (IOException e){

        }

        if (!noteHpoList.isEmpty()){
            insertBatchClinPhen(noteHpoList);
            noteHpoList.clear();
        }
    }

    public void initTableForClinPhen(){
        String query = "CREATE TABLE IF NOT EXISTS NoteHpoClinPhen(ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NOTES_ROW_ID INT, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
        jdbcTemplate.execute("TRUNCATE NoteHpoClinPhen;");
    }

    public void insertBatchClinPhen(final List<NoteHpo> noteHpos) {

        String sql = "INSERT INTO NoteHpoClinPhen " + "(NOTES_ROW_ID, NEGATED, MAP_TO) VALUES (?, ?, ?)";

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
