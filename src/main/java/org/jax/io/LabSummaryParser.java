package org.jax.io;

import org.jax.lab2hpo.LabSummary;

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
            String loinc = elements[2];
            int count = Integer.valueOf(elements[3]);
            Double mean = elements[4].equalsIgnoreCase("NULL") ? null : Double.valueOf(elements[4]);
            Double min_normal = elements[5].equalsIgnoreCase("NULL") ? null : Double.valueOf(elements[5]);
            Double max_normal = elements[7].equalsIgnoreCase("NULL") ? null : Double.valueOf(elements[7]);
            labSummaryMap.putIfAbsent(itemId, new LabSummary(itemId, loinc));
            labSummaryMap.get(itemId).put(unit, count, mean, min_normal, max_normal);
        }

        return labSummaryMap;
    }


}
