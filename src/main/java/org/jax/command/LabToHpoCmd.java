package org.jax.command;

import java.io.IOException;
import java.util.Map;

import org.jax.io.LabSummaryParser;
import org.jax.jdbc.Lab2HpoService;
import org.jax.lab2hpo.LabEvents2HpoFactory;
import org.jax.lab2hpo.LabSummary;
import org.monarchinitiative.loinc2hpo.io.LoincAnnotationSerializationFactory;
import org.monarchinitiative.loinc2hpo.loinc.LOINC2HpoAnnotationImpl;
import org.monarchinitiative.loinc2hpo.loinc.LoincEntry;
import org.monarchinitiative.loinc2hpo.loinc.LoincId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

/**
 * Class to convert laboratory tests into HPO terms
 */
@Parameters(commandDescription = "Convert Lab tests into Hpo")
public class LabToHpoCmd implements MimicCommand {

    private static final Logger logger = LoggerFactory.getLogger(LabToHpoCmd.class);
    
    @Autowired
    private Lab2HpoService lab2HpoService;

    @Parameter(names = {"-lab", "--lab_events"}, description = "file path to LABEVENTS.csv")
    private String labEventsPath;

    @Parameter(names = {"-lab_summary", "--lab_summary"}, description = "file path to lab summary")
    private String labSummaryPath;

    @Parameter(names = {"-annotation", "--loinc2hpoAnnotation"}, description = "file path to loinc2hpoAnnotation")
    String loinc2hpoAnnotationPath = null;

    @Parameter(names = {"-loincTable", "--loincCoreTable"}, description = "file path to loinc core table")
    String loincCoreTablePath = null;

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

        lab2HpoService.labToHpo(labConvertFactory);
    }
}
