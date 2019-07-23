package org.jax.jdbc;

import java.io.BufferedWriter;
import java.io.IOException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Optional;

import org.jax.Entity.LabEvent;
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
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;
import org.springframework.stereotype.Service;

@Service
public class Lab2HpoService {

	@Autowired
	JdbcTemplate jdbcTemplate;

	private final String allLabs = "select * from labevents";

	public void labToHpo(LabEvents2HpoFactory labConvertFactory, BufferedWriter writer) {
		// The fetch size will limit how many results come back at once reducing memory
		// requirements. This is the specific recommendation for MySQL and may need to be 
		// varied for other dbs
		jdbcTemplate.setFetchSize(Integer.MIN_VALUE);
		jdbcTemplate.query(allLabs, new LabEventCallbackHandler(jdbcTemplate, labConvertFactory, writer));
	}

	private class LabEventCallbackHandler implements RowCallbackHandler {

		JdbcTemplate jdbcTemplate;
		LabEvents2HpoFactory labConvertFactory;
		BufferedWriter writer;
		final String separator = ",";
		
		LabEventCallbackHandler(JdbcTemplate jdbcTemplate, LabEvents2HpoFactory labConvertFactory, BufferedWriter writer) {
			this.jdbcTemplate = jdbcTemplate;
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
	
				writer.write("\n");
				// Could be more efficient about this, but we'll replace this with db insert anyway
				writer.flush();
		} catch(Exception e) {
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

}

}
