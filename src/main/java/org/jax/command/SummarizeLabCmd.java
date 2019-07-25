package org.jax.command;

import java.io.BufferedWriter;
import java.io.IOException;
import java.util.List;

import org.jax.io.IoUtils;
import org.jax.jdbc.LabSummaryService;
import org.jax.lab2hpo.LabSummaryStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

/**
 * Query the LabEvents table and summarize lab statistics in a file, including mean and min and max values considered normal.
 * 
 * Arguments:
 * summarizeLab -o <outputFileLocation>
 * 
 * The resulting file contains the following columns:
 * - itemId: The local lab code for the system
 * - valueuom: A text description of the unit of measure
 * - loinc: The LOINC code for the lab
 * - mean_all: The mean value of all the labs with this itemId and unit
 * - min_normal: The minimum normal lab value found for this itemId and unit
 * - mean_normal: The mean normal lab value found for this itemId and unit
 * - max_normal: The maximum normal lab value found for this itemId and unit
 * 
 * @author yateam
 *
 */
@Parameters(commandDescription = "Summarize lab tests")
public class SummarizeLabCmd implements MimicCommand {
	
    private static final Logger logger = LoggerFactory.getLogger(SummarizeLabCmd.class);

    @Autowired
    private LabSummaryService labSummaryService;

    @Parameter(names = {"-o", "--output"}, description = "Output path")
    private String outPath;

	@Override
    public void run() {

		List<LabSummaryStatistics> stats = labSummaryService.labSummaryStatistics();

        BufferedWriter writer = IoUtils.getWriter(outPath);
        try {
        	writer.write("itemId\tvalueuom\tloinc\tmean_all\tmin_normal\tmean_normal\tmax_normal\n");
        } catch (IOException e) {
        	// Could not write header
        	logger.error("Could not write LabSummary header");
        }
        stats.stream().forEach(labSummary -> {
            try {
                writer.write(labSummary.getItemId() + "\t");
                writer.write(labSummary.getValueuom() + "\t");
                writer.write(labSummary.getLoinc() + "\t");
                writer.write(labSummary.getCounts() + "\t");
                writer.write((labSummary.getMean_all() == null ? "NULL":labSummary.getMean_all()) + "\t");
                writer.write((labSummary.getMin_normal() == null ? "NULL":labSummary.getMin_normal()) + "\t");
                writer.write((labSummary.getMean_normal() == null ? "NULL":labSummary.getMean_normal()) + "\t");
                writer.write((labSummary.getMax_normal()==null) ? "NULL":labSummary.getMax_normal().toString());
                writer.write("\n");
            } catch (IOException e) {
                e.printStackTrace();
            }
        });

        try {
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }


    }



}
