package org.jax.jdbc;

import java.io.BufferedWriter;
import java.io.IOException;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.jax.Entity.LabEvent;
import org.jax.Entity.LabHpo;
import org.jax.io.LabEventFactory;
import org.jax.lab2hpo.LabEvents2HpoFactory;
import org.jax.lab2hpo.UnableToInterpretateException;
import org.jax.lab2hpo.UnrecognizedUnitException;
import org.jax.service.LocalLabTestNotMappedToLoinc;
import org.monarchinitiative.loinc2hpo.exception.LoincCodeNotAnnotatedException;
import org.monarchinitiative.loinc2hpo.exception.MalformedLoincCodeException;
import org.monarchinitiative.loinc2hpo.exception.UnrecognizedCodeException;
import org.monarchinitiative.loinc2hpo.loinc.HpoTerm4TestOutcome;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;

@Service
public class Lab2HpoService {

	@Autowired
	JdbcTemplate jdbcTemplate;

	@Autowired
	private PlatformTransactionManager transactionManager;
	
	private final String allLabs = "select * from samplelabevents";

	public void labToHpo(LabEvents2HpoFactory labConvertFactory, BufferedWriter writer) {
		// The fetch size will limit how many results come back at once reducing memory
		// requirements. This is the specific recommendation for MySQL and may need to
		// be
		// varied for other dbs
		jdbcTemplate.setFetchSize(Integer.MIN_VALUE);
		initTable();
		jdbcTemplate.query(allLabs, new LabEventCallbackHandler(jdbcTemplate, transactionManager, labConvertFactory, writer));
	}

	public void initTable() {
		String query = "CREATE TABLE IF NOT EXISTS LABHPO (ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID));";
		jdbcTemplate.execute(query);
		jdbcTemplate.execute("TRUNCATE LABHPO;");
	}

	private class LabEventCallbackHandler implements RowCallbackHandler {

		JdbcTemplate jdbcTemplate;
		TransactionTemplate transactionTemplate;
		LabEvents2HpoFactory labConvertFactory;
		BufferedWriter writer;
		final String separator = ",";
		List<LabHpo> labHpos = new ArrayList<>();

		LabEventCallbackHandler(JdbcTemplate jdbcTemplate, PlatformTransactionManager transactionManager, LabEvents2HpoFactory labConvertFactory,
				BufferedWriter writer) {
			this.jdbcTemplate = jdbcTemplate;
			this.transactionTemplate = new TransactionTemplate(transactionManager);
			this.labConvertFactory = labConvertFactory;
			this.writer = writer;
		}

		@Override
		public void processRow(ResultSet rs) throws SQLException {

			if (rs.isFirst()) {
				try { // write header
					writer.write("ROW_ID,NEGATED,MAP_TO\n");
				} catch (IOException e) {
					e.printStackTrace();
					System.exit(1);
				}
			}
			try {
				LabEvent labEvent = LabEventFactory.parse(rs);
				int rowId = labEvent.getRow_id();
				writer.write(Integer.toString(labEvent.getRow_id()));
				writer.write(separator);

				Optional<HpoTerm4TestOutcome> outcome = null;
				try {
					outcome = labConvertFactory.convert(labEvent);
					boolean negated = false;
					String mappedHpo = "?";
					if (outcome.isPresent()) {
						negated = outcome.get().isNegated();
						mappedHpo = outcome.get().getId().getValue();
					}
					writer.write(negated ? "T" : "F");
					writer.write(separator);
					writer.write(mappedHpo);
					labHpos.add(new LabHpo(rowId, negated ? "T" : "F", mappedHpo));
				} catch (LocalLabTestNotMappedToLoinc e) {
					writer.write("U");
					writer.write(separator);
					writer.write("ERROR 1: local id not mapped to loinc");
				} catch (MalformedLoincCodeException e) {
					writer.write("U");
					writer.write(separator);
					writer.write("ERROR 2: malformed loinc id");
				} catch (LoincCodeNotAnnotatedException e) {
					writer.write("U");
					writer.write(separator);
					writer.write("ERROR 3: loinc code not annotated");
				} catch (UnrecognizedCodeException e) {
					writer.write("U");
					writer.write(separator);
					writer.write("ERROR 4: interpretation code not mapped to hpo");
				} catch (UnableToInterpretateException e) {
					writer.write("U");
					writer.write(separator);
					writer.write("ERROR 5: unable to interpret");
				} catch (UnrecognizedUnitException e) {
					writer.write("U");
					writer.write(separator);
					writer.write("ERROR 6: unrecognized unit");
				}

				if (labHpos.size() > 1000 || rs.isLast()) {
					insertBatch(labHpos);
					labHpos.clear();
				}

				writer.write("\n");
				// Could be more efficient about this, but we'll replace this with db insert
				// anyway
				writer.flush();
// TODO: Restore this?				
//		        if (printError) {
//	        	for (Integer f : labConvertFactory.getFailedQnWithTextResult()) {
//	                try {
//	                    writer.write(Integer.toString(f));
//	                    writer.write("\t");
//	                    String loinc = labSummaryMap.get(f).getLoinc();
//	                    writer.write(loinc == null ? "LOINC:[?]" : "LOINC:" + loinc);
//	                    writer.write("\n");
//	                } catch (IOException e) {
//	                    e.printStackTrace();
//	                }
//	        	}        	
//	        }

			} catch (Exception e) {
				e.printStackTrace();
			}

			if (rs.isLast()) {
				try { // Close the writer
					writer.close();
				} catch (IOException e) {
					e.printStackTrace();
					System.exit(1);
				}
			}

		}

		public void insertBatch(final List<LabHpo> labHpos) {

			String sql = "INSERT INTO LABHPO " + "(ROW_ID, NEGATED, MAP_TO) VALUES (?, ?, ?)";

			transactionTemplate.execute(new TransactionCallbackWithoutResult() {

				@Override
				protected void doInTransactionWithoutResult(TransactionStatus status) {			
					jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {


					@Override
					public void setValues(PreparedStatement ps, int i) throws SQLException {
						LabHpo labHpo = labHpos.get(i);
						ps.setInt(1, labHpo.getRowid());
						ps.setString(2, labHpo.getNegated());
						ps.setString(3, labHpo.getMapTo());
					}
	
					@Override
					public int getBatchSize() {
						return labHpos.size();
					}
				});
			}});
		}

	}

}
