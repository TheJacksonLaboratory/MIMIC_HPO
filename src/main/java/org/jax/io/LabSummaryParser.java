package org.jax.io;

import org.jax.LabSummary;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class LabSummaryParser {

    private String path;

    public LabSummaryParser(String path) {
        this.path = path;
    }

    public Map<Integer, LabSummary> parse() throws IOException {

        Map<Integer, LabSummary> labSummaryMap = new HashMap<>();

        BufferedReader reader = new BufferedReader(new FileReader(path));
        String line = reader.readLine();
        while ((line = reader.readLine()) != null){
            String[] elements = line.split("\t");
            int itemId = Integer.valueOf(elements[0]);
            String unit = elements[1];
            int count = Integer.valueOf(elements[2]);
            double mean = Double.valueOf(elements[3]);
            labSummaryMap.putIfAbsent(itemId, new LabSummary(itemId));
            labSummaryMap.get(itemId).put(unit, count, mean);
        }

        return labSummaryMap;
    }


}
