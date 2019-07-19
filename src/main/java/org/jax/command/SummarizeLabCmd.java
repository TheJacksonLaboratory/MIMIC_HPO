package org.jax.command;

import java.io.BufferedWriter;
import java.io.IOException;
import java.util.List;

import org.jax.LabSummaryService;
import org.jax.io.IoUtils;
import org.jax.lab2hpo.LabSummaryStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

@Parameters(commandDescription = "Summarize lab tests")
public class SummarizeLabCmd implements MimicCommand {
	
    private static final Logger logger = LoggerFactory.getLogger(SummarizeLabCmd.class);

    private LabSummaryService labSummaryService;

    @Parameter(names = {"-o", "--output"}, description = "Output path")
    private String outPath;

    public SummarizeLabCmd(LabSummaryService labSummaryService) {
		this.labSummaryService = labSummaryService;
	}

	@Override
    public void run() {

		long start = System.currentTimeMillis();
		List<LabSummaryStatistics> stats = labSummaryService.labSummaryStatistics();
		long finish = System.currentTimeMillis();
		logger.info("Summary statistics returned in " + (finish-start)/1000.0 + " seconds");

        BufferedWriter writer = IoUtils.getWriter(outPath);
        stats.stream().forEach(labSummary -> {
            try {
                writer.write(labSummary.getItemId() + "\t");
                writer.write(labSummary.getValueuom() + "\t");
                writer.write(labSummary.getLoinc() + "\t");
                writer.write(labSummary.getCounts() + "\t");
                writer.write(labSummary.getMean_all() + "\t");
                writer.write(labSummary.getMin_normal() + "\t");
                writer.write(labSummary.getMean_normal() + "\t");
                writer.write(labSummary.getMax_normal().toString());
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
