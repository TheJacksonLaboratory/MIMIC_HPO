package org.jax.jdbc;

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

	private final String allLabs = "select * from labevents";

	public void labToHpo(LabEvents2HpoFactory labConvertFactory) {
		// The fetch size will limit how many results come back at once reducing memory
		// requirements. This is the specific recommendation for MySQL and may need to
		// be
		// varied for other dbs
		jdbcTemplate.setFetchSize(Integer.MIN_VALUE);
		initTable();
		jdbcTemplate.query(allLabs,
				new LabEventCallbackHandler(jdbcTemplate, transactionManager, labConvertFactory));
	}

	public void initTable() {
		String query = "CREATE TABLE IF NOT EXISTS LABHPO (ROW_ID INT UNSIGNED NOT NULL AUTO_INCREMENT, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID));";
		jdbcTemplate.execute(query);
		jdbcTemplate.execute("TRUNCATE LABHPO;");
	}

	private class LabEventCallbackHandler implements RowCallbackHandler {

		int batchSize = 20000;
		JdbcTemplate jdbcTemplate;
		TransactionTemplate transactionTemplate;
		LabEvents2HpoFactory labConvertFactory;
		List<LabHpo> labHpos = new ArrayList<>(batchSize);

		LabEventCallbackHandler(JdbcTemplate jdbcTemplate, PlatformTransactionManager transactionManager,
				LabEvents2HpoFactory labConvertFactory) {
			this.jdbcTemplate = jdbcTemplate;
			this.transactionTemplate = new TransactionTemplate(transactionManager);
			this.labConvertFactory = labConvertFactory;
		}

		@Override
		public void processRow(ResultSet rs) throws SQLException {

			LabEvent labEvent = LabEventFactory.parse(rs);
			int rowId = labEvent.getRow_id();
			LabHpo labHpo = null;

			Optional<HpoTerm4TestOutcome> outcome = null;
			try {
				outcome = labConvertFactory.convert(labEvent);
				boolean negated = false;
				String mappedHpo = "?";
				if (outcome.isPresent()) {
					negated = outcome.get().isNegated();
					mappedHpo = outcome.get().getId().getValue();
				}
				labHpo = new LabHpo(rowId, negated ? "T" : "F", mappedHpo);
			} catch (LocalLabTestNotMappedToLoinc e) {
				labHpo = new LabHpo(rowId, "U", "ERROR 1: local id not mapped to loinc");
			} catch (MalformedLoincCodeException e) {
				labHpo = new LabHpo(rowId, "U", "ERROR 2: malformed loinc id");
			} catch (LoincCodeNotAnnotatedException e) {
				labHpo = new LabHpo(rowId, "U", "ERROR 3: loinc code not annotated");
			} catch (UnrecognizedCodeException e) {
				labHpo = new LabHpo(rowId, "U", "ERROR 4: interpretation code not mapped to hpo");
			} catch (UnableToInterpretateException e) {
				labHpo = new LabHpo(rowId, "U", "ERROR 5: unable to interpret");
			} catch (UnrecognizedUnitException e) {
				labHpo = new LabHpo(rowId, "U", "ERROR 6: unrecognized unit");
			}

			labHpos.add(labHpo);

			if (labHpos.size() == batchSize || rs.isLast()) {
				insertBatch(labHpos);
				labHpos.clear();
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
				}
			});
		}

	}

}
