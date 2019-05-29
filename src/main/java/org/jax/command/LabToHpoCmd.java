package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.Entity.LabDictItem;
import org.jax.Entity.LabEvent;
import org.jax.lab2hpo.LabSummary;
import org.jax.io.*;
import org.jax.lab2hpo.LabEvents2HpoFactory;
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

import java.io.*;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

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

    @Override
    public void run() {
        //How to?
        //input: lab record + summary file (obtain through running SummarizeLabCmd command)
        //for each lab record,
        //  read the "unit" field, discard if it is an outlier, unless it is one the three special cases
        //
        //  read the "flag" and "value" fields, and create a more meaningful "flag":
        //      if the "value" is not a number, keep the "flag" unchanged
        //      if the "value" is a number and the "flag" is abnormal, compare "value" with mean: assign "H" if value > mean, "L" otherwise.

        LabSummaryParser labSummaryparser = new LabSummaryParser(labSummaryPath);
        Map<Integer, LabSummary> labSummaryMap = null;
        try {
            labSummaryMap = labSummaryparser.parse();
        } catch (IOException e) {
            e.printStackTrace();
        }

        //get the local lab test code to loinc mapping
        String labDictPath = this.getClass().getClassLoader().getResource("D_LABITEMS.csv").getPath();
        LabDictParser labDictParser = new LabDictParser(labDictPath);
        Map<Integer, LabDictItem> labDictMap = null;
        try {
            labDictMap = labDictParser.parse();
        } catch (IOException e) {
            logger.error("local to loinc mapping failed loading. Exiting...");
            e.printStackTrace();
            System.exit(1);
        }
        Map<Integer, String> local2loinc = labDictMap.values().stream()
                .filter(labDictItem -> ! labDictItem.getLoincCode().isEmpty()) // some are not mapped to loinc
                .collect(
                Collectors.toMap(LabDictItem::getItemId, LabDictItem::getLoincCode));
        logger.info("local to loinc mapping successfully loaded");
//        local2loinc.entrySet().stream().map(e-> e.getKey().toString() + " -> " + e.getValue()).forEach(System.out::println);


        //get the primary unit for each lab test: unit with the maximum count
        //in most cases, there are two units, one is correct (dominant) and the other missing
        //we skip the missing one
//        Map<Integer, String> primaryUnits = labSummaryMap.values().stream().collect(Collectors.toMap(
//                labSummary -> labSummary.getId(),
//                labSummary -> labSummary.getCountByUnit().entrySet().stream()
//                        .sorted((x, y) -> y.getValue() - x.getValue()) //sort unit by counts, reverse
//                        .map(e -> e.getKey()).findFirst().orElse("SHOULD NEVER HAPPEN!")
//        ));
//        logger.info("primary units for each lab test successfully loaded");
//        logger.info("primary units - " + primaryUnits.size());


//        //find the mean for the primary units
//        Map<Integer, Double> primaryMeans = labSummaryMap.values().stream().collect(Collectors.toMap(
//                labSummary -> labSummary.getId(),
//                labSummary -> labSummary.getMeanByUnit()
//                        .get(primaryUnits.get(labSummary.getId()))
//        ));
//
//        logger.info("mean value for each lab test successfully loaded");
//        logger.info("primary means - " + primaryMeans.size());


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
//        LabEvents2HpoFactory labConvertFactory = new LabEvents2HpoFactory(
//                local2loinc,
//                primaryUnits,
//                primaryMeans,
//                annotationMap,
//                loincEntryMap
//        );

        LabEvents2HpoFactory labConvertFactory = new LabEvents2HpoFactory(
                local2loinc,
                labSummaryMap,
                annotationMap,
                loincEntryMap
        );

        BufferedWriter writer = IoUtils.getWriter(outPath);
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

                    final String separator = "\t";
                    writer.write(Integer.toString(labEvent.getRow_id()));
                    writer.write(separator);
                    writer.write(Integer.toString(labEvent.getItem_id()));
                    writer.write(separator);
                    writer.write(labEvent.getValue());
                    writer.write(separator);
                    writer.write(labEvent.getFlag());
                    writer.write(separator);


                    Optional<HpoTerm4TestOutcome> outcome = null;
                    try {
                        outcome = labConvertFactory.convert2(labEvent);
                        String mappedHpo = "?";
                        if (outcome.isPresent()) {
                            mappedHpo = outcome.get().getId().getValue();
                        }
                        writer.write(mappedHpo);
                    } catch (LocalLabTestNotMappedToLoinc e) {
                        writer.write("ERROR 1: local id not mapped to loinc");
                    } catch (MalformedLoincCodeException e) {
                        writer.write("ERROR 2: malformed loinc id");
                    } catch (LoincCodeNotAnnotatedException e) {
                        writer.write("ERROR 3: loinc code not annotated");
                    } catch (UnrecognizedCodeException e) {
                        writer.write("ERROR 4: interpretation code not mapped to hpo");
                    } catch (UnableToInterpretateException e) {
                        writer.write("ERROR 5: unable to interpret");
                    } catch (UnrecognizedUnitException e) {
                        writer.write("ERROR 6: unrecognized unit");
                    }

                    writer.write("\n");


                } catch (MimicHpoException e) {
                    logger.error("parsing error: " + line);
                }

                //debug with 10 records
                if (count > 10000) {
                    break;
                }
            }

        } catch (FileNotFoundException e){
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }


        System.out.println("Lab to HPO started " + outPath);

    }
}
