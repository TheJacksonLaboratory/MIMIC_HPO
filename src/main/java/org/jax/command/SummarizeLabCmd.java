package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.Entity.LabDictItem;
import org.jax.LabSummary;
import org.jax.io.IoUtils;
import org.jax.io.LabDictParser;
import org.jax.io.QnLabSummarize;
import org.jax.service.LabDictService;
import org.jax.service.LabDictServiceImpl;
import org.jax.service.LabSummaryService;
import org.jax.io.QnLabSummarizeFileImpl;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.Map;

@Parameters(commandDescription = "Summarize lab tests")
public class SummarizeLabCmd implements MimicCommand {

    @Parameter(names = {"-lab", "--lab_events"}, description = "file path to LABEVENTS.csv")
    private String labEventsPath;

    @Parameter(names = {"-dict", "--lab_dict"}, description = "file path to D_LABITEMS.csv")
    private String labDictPath;

    @Parameter(names = {"-o", "--output"}, description = "Output path")
    private String outPath;

    @Override
    public void run() {
        //input: lab test records
        //count records by units for each lab test
        //calculate mean by units for each lab test

        //read in local lab test mapping file
        LabDictParser labDictParser = new LabDictParser(labDictPath);
        Map<Integer, LabDictItem> labDictItemMap = null;
        try {
            labDictItemMap = labDictParser.parse();
        } catch (IOException e) {
            e.printStackTrace();
        }

        LabDictService labDictService = new LabDictServiceImpl(labDictItemMap);

        //summarize quantitative lab test
        QnLabSummarize qnLabSummarize = new QnLabSummarizeFileImpl(labEventsPath);
        Map<Integer, LabSummary> labSummaryMap = null;
        try {
            labSummaryMap = qnLabSummarize.summarize();
        } catch (Exception e) {
            e.printStackTrace();
        }


        BufferedWriter writer = IoUtils.getWriter(outPath);
        labSummaryMap.entrySet().stream().limit(10).forEach(labSummary -> {
            try {
                writer.write(labDictService.loincOf(labSummary.getKey()).orElse("unknown loinc"));
                writer.write("\t");
                writer.write(labSummary.getValue().toString());
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
