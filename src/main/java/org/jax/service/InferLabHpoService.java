package org.jax.service;

import org.jax.Entity.LabHpo;
import org.monarchinitiative.phenol.ontology.algo.OntologyAlgorithm;
import org.monarchinitiative.phenol.ontology.data.TermId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.PreparedStatementCreator;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;
import org.springframework.jdbc.datasource.DataSourceUtils;
import org.springframework.lang.Nullable;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.lang.reflect.Parameter;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;


@Service
public class InferLabHpoService {

    @Autowired
    JdbcTemplate jdbcTemplate;

    @Autowired @Lazy
    HpoService hpoService;

    public int[] id_range(){
        int min = jdbcTemplate.queryForObject("SELECT min(ROW_ID) FROM LabHpo", Integer.class);
        int max = jdbcTemplate.queryForObject("SELECT max(ROW_ID) FROM LabHpo", Integer.class);
        return new int[] {min, max};
    }

    public void initTable(){
        String query = "CREATE TABLE IF NOT EXISTS INFERRED_LABHPO (ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, LABEVENT_ROW_ID INT UNSIGNED NOT NULL, INFERRED_TO VARCHAR(12), PRIMARY KEY (ROW_ID))";
        jdbcTemplate.execute(query);
    }

    public void infer(int batch_size) throws SQLException{

        Connection conn = DataSourceUtils.getConnection(jdbcTemplate.getDataSource());
        PreparedStatement pstmt = conn.prepareStatement("INSERT INTO INFERRED_LABHPO (LABEVENT_ROW_ID, INFERRED_TO) VALUES(?,?)");

        conn.setAutoCommit(false);

        String query = "SELECT * FROM LabHpo WHERE ROW_ID = ?";
        String query_batch = "SELECT * FROM LabHpo WHERE ROW_ID BETWEEN ? AND ? AND NEGATED = 'F'";
        int[] range = id_range();
        int START_INDEX = range[0];
        int END_INDEX = range[1];
        int BATCH_SIZE = batch_size;
        int BATCH = (END_INDEX - START_INDEX + 1) / BATCH_SIZE + 1;
        int total_count = 0;
        int to_commit_count = 0;
        for (int i = 0; i < BATCH; i++) {
            List<LabHpo> labHpoList = jdbcTemplate.query(query_batch, new Object[]{i * BATCH_SIZE, (i + 1) * BATCH_SIZE - 1}, new RowMapper<LabHpo>() {
                @Override
                public LabHpo mapRow(ResultSet rs, int rowNum) throws SQLException {
                    LabHpo labHpo = new LabHpo(rs.getInt("ROW_ID"),
                            rs.getString("NEGATED").charAt(0),
                            rs.getString("MAP_TO"));
                    return labHpo;
                }
            });

            List<Object[]> parameters = new ArrayList<>();
            for (LabHpo instance : labHpoList){
                if (instance.getMapTo().startsWith("HP:")) {
                    int labevent_row_id = instance.getRowid();
                    TermId termId = TermId.of(instance.getMapTo());
                    Set<TermId> parents = hpoService.infer(termId, false);
                    for (TermId parent : parents) {
                        Object[] values = new Object[]{
                                labevent_row_id, //ROW_ID from LabEvents
                                parent.getValue() //parent HPO term id
                        };
                        parameters.add(values);
                    }
                }
            }
            total_count += parameters.size();
            to_commit_count += parameters.size();
            if (i % 200000 == 0){
                System.out.println("batch: " + i);
                System.out.println("LabHpo list size: " + labHpoList.size());
                labHpoList.forEach(labhpo -> {
                    System.out.println(labhpo.getRowid() + "\t" + labhpo.getNegated() + "\t" + labhpo.getMapTo());
                });
                System.out.println("batch update size: " + parameters.size());
                parameters.forEach(p -> {
                    System.out.println(p[0] + "\t" + p[1]);
                });
            }

//            jdbcTemplate.batchUpdate("INSERT INTO INFERRED_LABHPO (LABEVENT_ROW_ID, INFERRED_TO) VALUES(?,?)", new BatchPreparedStatementSetter() {
//                @Override
//                public void setValues(PreparedStatement ps, int i) throws SQLException {
//                    Object[] parameter = parameters.get(i);
//                    ps.setInt(1, (Integer) parameter[0]);
//                    ps.setString(2, (String) parameter[1]);
//                }
//
//                @Override
//                public int getBatchSize() {
//                    return parameters.size();
//                }
//            });

            for (Object[] objects : parameters){
                pstmt.setInt(1, (Integer) objects[0]);
                pstmt.setString(2, (String) objects[1]);
                pstmt.executeUpdate();
            }

            if (to_commit_count > 10000){
                conn.commit();
                to_commit_count = 0;
                System.out.println("total derived HPO: " + total_count);
            }

//            try {
//                batchInsert(parameters);
//            } catch (SQLException e) {
//                e.printStackTrace();
//                throw new RuntimeException("SQL insertion error");
//            }
        }

        if (!conn.getAutoCommit()){
            conn.commit();
        }

        conn.setAutoCommit(true);
        System.out.println("new table size: " + total_count);
    }

    public void infer() throws SQLException{
        infer(1000);
    }

    public void batchInsert(List<Object[]> parameters) throws SQLException {
        Connection conn = DataSourceUtils.getConnection(jdbcTemplate.getDataSource());
        PreparedStatement pstmt = conn.prepareStatement("INSERT INTO INFERRED_LABHPO (LABEVENT_ROW_ID, INFERRED_TO) VALUES(?,?)");

        conn.setAutoCommit(false);

        for (Object[] objects : parameters){
            pstmt.setInt(1, (Integer) objects[0]);
            pstmt.setString(2, (String) objects[1]);
            pstmt.executeUpdate();
        }

        conn.setAutoCommit(true);


    }

}
