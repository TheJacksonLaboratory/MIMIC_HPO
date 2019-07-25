package org.jax.service;

import org.jax.Entity.InferredLabHpo;
import org.jax.Entity.LabHpo;
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


@Service
public class InferLabHpoService {

    static final Logger logger = LoggerFactory.getLogger(InferLabHpoService.class);

    @Autowired
    JdbcTemplate jdbcTemplate;

    @Autowired
    TransactionTemplate transactionTemplate;

    @Autowired @Lazy
    HpoService hpoService;

    /**
     * Check if the LabHpo table is empty
     * @return if LabHpo table is empty
     */
    private boolean isLabHpoEmpty(){
        int rowcount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM LabHpo", Integer.class);
        return rowcount==0;
    }

    // Get the range of ROW_ID (primary key) for the LabHpo table
    public int[] id_range(){
        Integer min = jdbcTemplate.queryForObject("SELECT min(ROW_ID) FROM LabHpo", Integer.class);
        Integer max = jdbcTemplate.queryForObject("SELECT max(ROW_ID) FROM LabHpo", Integer.class);
        return new int[] {min == null ? 0 : min, max == null ? 0 : max};
    }

    public void initTable(){
        String query = "CREATE TABLE IF NOT EXISTS INFERRED_LABHPO (ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, LABEVENT_ROW_ID INT UNSIGNED NOT NULL, INFERRED_TO VARCHAR(12), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
        jdbcTemplate.execute("TRUNCATE TABLE INFERRED_LABHPO");
    }

    public void infer(int batch_size){

        if(isLabHpoEmpty()){
            return;
        }

        String query_batch = "SELECT * FROM LabHpo WHERE ROW_ID BETWEEN ? AND ? AND NEGATED = 'F'";
        int[] range = id_range();
        int START_INDEX = range[0];
        int END_INDEX = range[1];
        int BATCH_SIZE = batch_size;
        int BATCH = (END_INDEX - START_INDEX + 1) / BATCH_SIZE + 1;
        int total_count = 0;
        for (int i = 0; i < BATCH; i++) {
            List<LabHpo> labHpoList = jdbcTemplate.query(query_batch, new Object[]{i * BATCH_SIZE, (i + 1) * BATCH_SIZE - 1}, new RowMapper<LabHpo>() {
                @Override
                public LabHpo mapRow(ResultSet rs, int rowNum) throws SQLException {
                    LabHpo labHpo = new LabHpo(rs.getInt("ROW_ID"),
                            rs.getString("NEGATED"),
                            rs.getString("MAP_TO"));
                    return labHpo;
                }
            });

            List<InferredLabHpo> inferredList = new ArrayList<>();

            labHpoList.stream()
                    //just handle those that successfully mapped to an HPO term
                    .filter(labHpo -> labHpo.getMapTo().startsWith("HP:"))
                    //infer the parent terms for each mapped HPO
                    //put the inferred HPO into a list for batch insert
                    .forEach(labHpo -> {
                        int labevent_row_id = labHpo.getRowid();
                        TermId termId = TermId.of(labHpo.getMapTo());
                        Set<TermId> parents = hpoService.infer(termId, false);
                        parents.stream()
                                .map(p -> new InferredLabHpo(labevent_row_id, p.getValue()))
                                .forEach(inferredList::add);
                    });

            batchInsert(inferredList);
            total_count += inferredList.size();
        }

        logger.info("new table size: " + total_count);
    }

    public void batchInsert(List<InferredLabHpo> inferredList){
        String query = "INSERT INTO INFERRED_LABHPO (LABEVENT_ROW_ID, INFERRED_TO) VALUES(?,?)";
        transactionTemplate.execute(new TransactionCallbackWithoutResult() {
            @Override
            protected void doInTransactionWithoutResult(TransactionStatus status) {
                jdbcTemplate.batchUpdate(query, new BatchPreparedStatementSetter() {
                    @Override
                    public void setValues(PreparedStatement ps, int i) throws SQLException {
                        InferredLabHpo inferredLabHpo = inferredList.get(i);
                        ps.setInt(1, inferredLabHpo.getForeign_id());
                        ps.setString(2, inferredLabHpo.getInferred_to());
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
        boolean exists = DatabaseIndexLookUpUtil.indexExists("Inferred_LabHpo", "Inferred_LabHpo_idx01", jdbcTemplate);
        if (!exists){
            jdbcTemplate.execute("CREATE INDEX Inferred_LabHpo_idx01 ON INFERRED_LABHPO (LABEVENT_ROW_ID);");
        }
    }

}
