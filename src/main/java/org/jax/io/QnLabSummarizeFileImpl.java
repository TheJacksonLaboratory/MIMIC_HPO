package org.jax.io;

import org.jax.LabSummary;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class QnLabSummarizeFileImpl implements QnLabSummarize {

    private static final Logger logger = LoggerFactory.getLogger(QnLabSummarizeFileImpl.class);

    private String labFilePath;


    public QnLabSummarizeFileImpl(String labFilePath) {
        this.labFilePath = labFilePath;
    }

    /**
     * Summarize quantitative lab tests
     * @return a map: key-local lab code; value: a LabSummary instance for current lab
     * @throws IOException
     */
    @Override
    public Map<Integer, LabSummary> summarize() throws IOException {

        Map<Integer, LabSummary> labSummaryMap = new HashMap<>();

        BufferedReader reader = new BufferedReader(new FileReader(this.labFilePath));
        String line = reader.readLine();

        int count = 0;
        while ((line = reader.readLine()) != null) {
            count++;
            if (count % 1000000 == 0) {
                logger.info("total lab events processed: " + count);
            }

            if (line.endsWith(",")) {
                line = line + " ";
            }
            String[] elements = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");

            try {
                int itemId = Integer.valueOf(elements[3].trim());
                if (elements[6].isEmpty()){
                    continue;//skip if this is not a quantitative test
                }
                double valueNum = Double.valueOf(elements[6]);
                String unit = elements[7].toLowerCase().replace("\"", "").trim();
                if (unit.isEmpty()) {
                    unit = "?"; //replace empty unit with "?"
                }
                labSummaryMap.putIfAbsent(itemId, new LabSummary(itemId));
                labSummaryMap.get(itemId).add(unit, valueNum);
            } catch (Exception e) {
                logger.warn("string to double conversion error (line skipped): " + line);
            }
        }

        return labSummaryMap;
    }

}
