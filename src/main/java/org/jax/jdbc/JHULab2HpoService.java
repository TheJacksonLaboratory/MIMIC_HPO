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
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.support.EncodedResource;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;
import org.springframework.jdbc.datasource.init.ScriptUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;

@Service
public class JHULab2HpoService {

	@Autowired
	JdbcTemplate jdbcTemplate;

	@Autowired
	private PlatformTransactionManager transactionManager;

	private final String maxRowIdQuery = "select max(row_id) from dbo.vw_pc_labs";
	private final String allLabsQuery = "select * from dbo.vw_pc_labs";

	public void labToHpo(JHULabView2HpoFactory labConvertFactory) {
		// The fetch size will limit how many results come back at once reducing memory
		// requirements. This is the specific recommendation for MySQL and may need to
		// be varied for other dbs
		jdbcTemplate.setFetchSize(Integer.MIN_VALUE);
		initTable();
		try {
			initErrorTable();
		} catch (SQLException e) {
			e.printStackTrace();
			//TODO: warn user
			return;
		}
		Integer maxRowId = jdbcTemplate.queryForObject(maxRowIdQuery, null, Integer.class);
		jdbcTemplate.query(allLabsQuery,
				new LabCallbackHandler(jdbcTemplate, transactionManager, labConvertFactory, maxRowId));
	}

	public void initTable() {
		String query = "CREATE TABLE IF NOT EXISTS LABHPO (ROW_ID INT UNSIGNED NOT NULL, NEGATED VARCHAR(5), MAP_TO VARCHAR(255), PRIMARY KEY (ROW_ID));";
		jdbcTemplate.execute(query);
		jdbcTemplate.execute("TRUNCATE LABHPO;");
	}

	public void initErrorTable() throws SQLException {
		EncodedResource script = new EncodedResource(new ClassPathResource("sql/errortable.sql"));
		ScriptUtils.executeSqlScript(jdbcTemplate.getDataSource().getConnection(), script);
	}

	private class LabCallbackHandler implements RowCallbackHandler {

		int batchSize = 20000;
		JdbcTemplate jdbcTemplate;
		TransactionTemplate transactionTemplate;
		JHULabView2HpoFactory labConvertFactory;
		Integer maxRowId;
		List<LabHpo> labHpos = new ArrayList<>(batchSize);

		LabCallbackHandler(JdbcTemplate jdbcTemplate, PlatformTransactionManager transactionManager,
				JHULabView2HpoFactory labConvertFactory, Integer maxRowId) {
			this.jdbcTemplate = jdbcTemplate;
			this.transactionTemplate = new TransactionTemplate(transactionManager);
			this.labConvertFactory = labConvertFactory;
			this.maxRowId = maxRowId;
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
				//ERROR 1: local id not mapped to loinc
				//Look up the D_LAB2HPO_MAP_ERR table for error code
				labHpo = new LabHpo(rowId, "U", "ERROR1");
			} catch (MalformedLoincCodeException e) {
				//ERROR 2: malformed loinc id
				labHpo = new LabHpo(rowId, "U", "ERROR2");
			} catch (LoincCodeNotAnnotatedException e) {
				//ERROR 3: loinc code not annotated
				labHpo = new LabHpo(rowId, "U", "ERROR3");
			} catch (UnrecognizedCodeException e) {
				//ERROR 4: interpretation code not mapped to hpo
				labHpo = new LabHpo(rowId, "U", "ERROR4");
			} catch (UnableToInterpretateException e) {
				//ERROR 5: unable to interpret
				labHpo = new LabHpo(rowId, "U", "ERROR5");
			} catch (UnrecognizedUnitException e) {
				//ERROR 6: unrecognized unit
				labHpo = new LabHpo(rowId, "U", "ERROR6");
			}

			labHpos.add(labHpo);
			
			if (labHpos.size() == batchSize || maxRowId.equals(rowId)) {
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
