package org.jax.command;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Map;
import java.util.Optional;

import org.jax.Entity.LabEvent;
import org.jax.io.IoUtils;
import org.jax.io.LabEventFactory;
import org.jax.io.LabSummaryParser;
import org.jax.io.MimicHpoException;
import org.jax.lab2hpo.LabEvents2HpoFactory;
import org.jax.lab2hpo.LabSummary;
import org.jax.lab2hpo.UnableToInterpretateException;
import org.jax.lab2hpo.UnrecognizedUnitException;
import org.jax.service.LocalLabTestNotMappedToLoinc;
import org.monarchinitiative.loinc2hpo.exception.LoincCodeNotAnnotatedException;
import org.monarchinitiative.loinc2hpo.exception.MalformedLoincCodeException;
import org.monarchinitiative.loinc2hpo.exception.UnrecognizedCodeException;
import org.monarchinitiative.loinc2hpo.io.LoincAnnotationSerializationFactory;
import org.monarchinitiative.loinc2hpo.loinc.HpoTerm4TestOutcome;
import org.monarchinitiative.loinc2hpo.loinc.LOINC2HpoAnnotationImpl;
import org.monarchinitiative.loinc2hpo.loinc.LoincEntry;
import org.monarchinitiative.loinc2hpo.loinc.LoincId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

/**
 * Class to convert laboratory tests into HPO terms
 */
@Parameters(commandDescription = "Convert Lab tests into Hpo")
public class LabToHpoCmd implements MimicCommand {

    private static final Logger logger = LoggerFactory.getLogger(LabToHpoCmd.class);

    @Parameter(names = {"-lab", "--lab_events"}, description = "file path to LABEVENTS.csv")
    private String labEventsPath;

    @Parameter(names = {"-lab_summary", "--lab_summary"}, description = "file path to lab summary")
    private String labSummaryPath;

    @Parameter(names = {"-annotation", "--loinc2hpoAnnotation"}, description = "file path to loinc2hpoAnnotation")
    String loinc2hpoAnnotationPath = null;

    @Parameter(names = {"-loincTable", "--loincCoreTable"}, description = "file path to loinc core table")
    String loincCoreTablePath = null;

    @Parameter(names = {"-o", "--output"}, description = "Output path")
    private String outPath;

    @Parameter(names = {"-error", "--error"}, description = "Print out some error messages")
    private boolean printError = false;

    @Override
    public void run() {

        LabSummaryParser labSummaryparser = new LabSummaryParser(labSummaryPath);
        Map<Integer, LabSummary> labSummaryMap = null;
        try {
            labSummaryMap = labSummaryparser.parse();
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }

        Map<LoincId, LOINC2HpoAnnotationImpl> annotationMap = null;
        try {
            annotationMap = LoincAnnotationSerializationFactory.parseFromFile(loinc2hpoAnnotationPath, null, LoincAnnotationSerializationFactory.SerializationFormat.TSVSingleFile);
        } catch (Exception e) {
            logger.error("loinc2hpoAnnotation failed to load");
            e.printStackTrace();
            System.exit(1);
        }
        logger.info("loinc2hpoAnnotation successfully loaded.");
        logger.info("Total annotations: " + annotationMap.size());


        //load loincCoreTable
        Map<LoincId, LoincEntry> loincEntryMap = LoincEntry.getLoincEntryList(loincCoreTablePath);
        if (loincEntryMap.isEmpty()) {
            logger.error("loinc core table failed to load");
            System.exit(1);
        } else {
            logger.info("loinc core table successfully loaded");
            logger.info("loinc entries: " + loincEntryMap.size());
        }

        //start processing
        LabEvents2HpoFactory labConvertFactory = new LabEvents2HpoFactory(
                labSummaryMap,
                annotationMap,
                loincEntryMap
        );

        BufferedWriter writer = IoUtils.getWriter(outPath);
        try { // write header
            writer.write("ROW_ID,NEGATED,MAP_TO\n");
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
        
        int count = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(labEventsPath))){
            String line = reader.readLine();
            while ((line = reader.readLine()) != null) {
                count++;
                if (count % 1000000 == 0) {
                    logger.info("total lines processed: " + count);
                }
                try {
                    LabEvent labEvent = LabEventFactory.parse(line);

                    final String separator = ",";
                    writer.write(Integer.toString(labEvent.getRow_id()));
                    writer.write(separator);
                    //writer.write(Integer.toString(labEvent.getItem_id()));
                    //writer.write(separator);
                    //writer.write(labEvent.getValue());
                    //writer.write(separator);
                    //writer.write(labEvent.getFlag());
                    //writer.write(separator);


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
                } catch (MimicHpoException e) {
                    logger.error("parsing error: " + line);
                }

                //debug with 10 records
                if (count > Integer.MAX_VALUE) {
                    break;
                }
            }

        } catch (FileNotFoundException e){
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        if (printError) {
        	for (Integer f : labConvertFactory.getFailedQnWithTextResult()) {
                try {
                    writer.write(Integer.toString(f));
                    writer.write("\t");
                    String loinc = labSummaryMap.get(f).getLoinc();
                    writer.write(loinc == null ? "LOINC:[?]" : "LOINC:" + loinc);
                    writer.write("\n");
                } catch (IOException e) {
                    e.printStackTrace();
                }
        	}        	
        }

        try {
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
