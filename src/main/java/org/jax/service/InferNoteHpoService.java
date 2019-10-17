package org.jax.service;

import org.jax.Entity.InferredLabHpo;
import org.jax.Entity.InferredNoteHpo;
import org.jax.Entity.LabHpo;
import org.jax.Entity.NoteHpo;
import org.jax.util.DatabaseIndexLookUpUtil;
import org.monarchinitiative.phenol.ontology.data.TermId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * TODO: thins class is almost identical to InferLabHpoService. We should abstract them into one.
 */
@Service
public class InferNoteHpoService {

    static final Logger logger = LoggerFactory.getLogger(InferLabHpoService.class);

    @Autowired
    JdbcTemplate jdbcTemplate;

    @Autowired
    TransactionTemplate transactionTemplate;

    @Autowired @Lazy
    HpoService hpoService;

    /**
     * Check if the NoteHpoClinPhen table is empty
     * @return if NoteHpoClinPhen table is empty
     */
    private boolean isNoteHpoEmpty(){
        int rowcount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM NoteHpoClinPhen", Integer.class);
        return rowcount==0;
    }

    // Get the range of ROW_ID (primary key) for the NoteHpo table
    public int[] id_range(){
        Integer min = jdbcTemplate.queryForObject("SELECT min(ROW_ID) FROM NoteHpoClinPhen", Integer.class);
        Integer max = jdbcTemplate.queryForObject("SELECT max(ROW_ID) FROM NoteHpoClinPhen", Integer.class);
        return new int[] {min == null ? 0 : min, max == null ? 0 : max};
    }

    public void initTable(){
        String query = "CREATE TABLE IF NOT EXISTS INFERRED_NoteHpo (ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NOTEEVENT_ROW_ID INT UNSIGNED NOT NULL, INFERRED_TO VARCHAR(12), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
        jdbcTemplate.execute("TRUNCATE TABLE INFERRED_NoteHpo");
    }

    public void infer(int batch_size){

        if(isNoteHpoEmpty()){
            return;
        }

        String query_batch = "SELECT * FROM NoteHpoClinPhen WHERE ROW_ID BETWEEN ? AND ? AND NEGATED = 'F'";
        int[] range = id_range();
        int START_INDEX = range[0];
        int END_INDEX = range[1];
        int BATCH_SIZE = batch_size;
        int BATCH = (END_INDEX - START_INDEX + 1) / BATCH_SIZE + 1;
        int total_count = 0;
        for (int i = 0; i < BATCH; i++) {
            List<NoteHpo> noteHpoList = jdbcTemplate.query(query_batch, new Object[]{i * BATCH_SIZE, (i + 1) * BATCH_SIZE - 1}, new RowMapper<NoteHpo>() {
                @Override
                public NoteHpo mapRow(ResultSet rs, int rowNum) throws SQLException {
                    NoteHpo noteHpo = new NoteHpo(rs.getInt("ROW_ID"),
                            rs.getInt("NOTES_ROW_ID"),
                            rs.getString("NEGATED"),
                            rs.getString("MAP_TO"));
                    return noteHpo;
                }
            });

            List<InferredNoteHpo> inferredList = new ArrayList<>();

            noteHpoList.stream()
                    //infer the parent terms for each mapped HPO
                    //put the inferred HPO into a list for batch insert
                    .forEach(noteHpo -> {
                        int noteevent_row_id = noteHpo.getRowid();
                        TermId termId = TermId.of(noteHpo.getMapTo());
                        Set<TermId> parents = hpoService.infer(termId, false);
                        parents.stream()
                                .map(p -> new InferredNoteHpo(noteevent_row_id, p.getValue()))
                                .forEach(inferredList::add);
                    });

            batchInsert(inferredList);
            total_count += inferredList.size();
        }

        logger.info("new table size: " + total_count);
    }

    public void batchInsert(List<InferredNoteHpo> inferredList){
        String query = "INSERT INTO INFERRED_NoteHpo (NOTEEVENT_ROW_ID, INFERRED_TO) VALUES(?,?)";
        transactionTemplate.execute(new TransactionCallbackWithoutResult() {
            @Override
            protected void doInTransactionWithoutResult(TransactionStatus status) {
                jdbcTemplate.batchUpdate(query, new BatchPreparedStatementSetter() {
                    @Override
                    public void setValues(PreparedStatement ps, int i) throws SQLException {
                        InferredNoteHpo inferredNoteHpo = inferredList.get(i);
                        ps.setInt(1, inferredNoteHpo.getForeign_id());
                        ps.setString(2, inferredNoteHpo.getInferred_to());
                    }

                    @Override
                    public int getBatchSize() {
                        return inferredList.size();
                    }
                });
            }
        });
    }

    public void createIndexOnForeignKey(){
        boolean exists = DatabaseIndexLookUpUtil.indexExists("Inferred_NoteHpo", "Inferred_NoteHpo_idx01", jdbcTemplate);
        if (!exists){
            jdbcTemplate.execute("CREATE INDEX Inferred_NoteHpo_idx01 ON INFERRED_NoteHpo (NOTEEVENT_ROW_ID);");
        }
    }

}
