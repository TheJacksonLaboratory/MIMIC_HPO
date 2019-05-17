package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.Entity.LabEvents;
import org.jax.LabSummary;
import org.jax.io.IoUtils;
import org.jax.io.LabEventFactory;
import org.jax.io.LabSummaryParser;
import org.jax.io.MimicHpoException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.util.Map;
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

    @Parameter(names = {"-o", "--output"}, description = "Output path")
    private String outPath;

    @Override
    public void run() {
        //How to?
        //input: lab record + summary file (obtain through running SummarizeLabCmd command)
        //for each lab record,
        //  read the "unit" filed, discard if it is an outlier, unless it is one the three special cases
        //
        //read the "flag" and "value" fields, and create a more meaningful "flag":
        //  if the "value" is not a number, keep the "flag" unchanged
        //  if the "value" is a number and the "flag" is abnormal, compare "value" with mean: assign "H" if value > mean, "L" otherwise.

        LabSummaryParser labSummaryparser = new LabSummaryParser(labSummaryPath);
        Map<Integer, LabSummary> labSummaryMap = null;
        try {
            labSummaryMap = labSummaryparser.parse();
        } catch (IOException e) {
            e.printStackTrace();
        }

        //get the primary unit for each lab test: unit with the maximum count
        //in most cases, there are two units, one is correct (dominant) and the other missing
        //we skip the missing one
        Map<Integer, String> primaryUnits = labSummaryMap.values().stream().collect(Collectors.toMap(
                labSummary -> labSummary.getId(),
                labSummary -> labSummary.getCountByUnit().entrySet().stream()
                        .sorted((x, y) -> y.getValue() - x.getValue()) //sort unit by counts, reverse
                        .map(e -> e.getKey()).findFirst().orElse("SHOULD NEVER HAPPEN!")
        ));

        //find the mean for the primary units
        Map<Integer, Double> primaryMeans = labSummaryMap.values().stream().collect(Collectors.toMap(
                labSummary -> labSummary.getId(),
                labSummary -> labSummary.getMeanByUnit()
                        .get(primaryUnits.get(labSummary.getId()))
        ));

        logger.info("Lab summary loaded: primary units - " + primaryUnits.size());
        logger.info("Lab summary loaded: primary means - " + primaryMeans.size());

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
                    LabEvents labEvents = LabEventFactory.parse(line);
                    writer.write(labEvents.getItem_id() + "\t" + labEvents.getFlag());

                } catch (MimicHpoException e) {
                    logger.error("parsing error: " + line);
                }
            }

        } catch (FileNotFoundException e){

        } catch (IOException e) {

        }





        System.out.println("Lab to HPO started " + outPath);

    }
}
