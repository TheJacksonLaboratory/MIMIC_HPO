package org.jax;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Hello world!
 *
 */
public class App {

    static Map<String, Integer> labItemCounts(String filepath) {
        Map<String, Integer> itemCounts = new HashMap<>();

        int count = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String line = reader.readLine();
            while ((line = reader.readLine()) != null) {
                if (line.endsWith(",")){
                    line = line + " ";
                }

                //split by comma unless it is inside quotes
                //ref: https://stackabuse.com/regex-splitting-by-character-unless-in-quotes/
                String[] elements = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");
                if (elements.length != 9) {
                    System.out.println("line: " + line);
                    System.out.println("number of fields: " + elements.length);
                    Arrays.stream(elements).forEach(e -> System.out.print(" [" + e + "] "));
                    System.out.println("");
                }

                String itemId = elements[3];
                itemCounts.putIfAbsent(itemId, 0);
                itemCounts.put(itemId, itemCounts.get(itemId) + 1);
                count++;
                if (count % 1000000 == 0) {
                    System.out.println("total processed lines: " + count);
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return itemCounts;
    }

    static Map<String, String> itemToLoinc(String path) {

        Map<String, String> itemToLoincMap = new HashMap<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            String line = reader.readLine();
            while ((line = reader.readLine()) != null) {
                if (line.endsWith(",")) {
                    line = line + " ";
                }
                String[] elements = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");
                if (elements.length != 6){
                    System.out.println("line does not have 6 fields: " + line);
                }

                String itemId = elements[1];
                String loinc = elements[5].replace("\"", "");
//                if (loinc.trim().isEmpty()) {
//                    System.out.println(line);
//                }
                if (!loinc.trim().isEmpty()){
                    itemToLoincMap.putIfAbsent(itemId, loinc);
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return itemToLoincMap;

    }

    static Map<String, Lab> summarize(String path) {
        Map<String, Lab> units = new HashMap<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            String line = reader.readLine();
            while ((line = reader.readLine()) != null) {
                if (line.endsWith(",")) {
                    line = line + " ";
                }
                String[] elements = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");
                String itemId = elements[3];
                String unit = elements[7].toLowerCase().replace("\"", "").trim();
                unit = unit.isEmpty()? "empty" : unit;
                String valueString = elements[6].trim();
                try {
                    double value = Double.valueOf(valueString);
                    units.putIfAbsent(itemId, new Lab(itemId));
                    units.get(itemId).add(unit, value);
                } catch (Exception e) {
                    System.out.println(line);
                    //skip
                }

            }
        } catch (FileNotFoundException e) {

        } catch (IOException e) {
            e.printStackTrace();
        }

        return units;
    }

    public static void main( String[] args ) {

        String lab_path = "/Users/zhangx/git/MIMIC_HPO/src/main/resources/LABEVENTS.csv";
        String lab_items_path = "/Users/zhangx/git/MIMIC_HPO/src/main/resources/D_LABITEMS.csv";
//        Map<String, Integer> itemCounts = labItemCounts(lab_path);
        Map<String, String> itemLoincMap = itemToLoinc(lab_items_path);
        Map<String, Lab> units = summarize(lab_path);

//        int TOTAL_LABS = itemCounts.values().stream().reduce((e1, e2) -> e1 + e2).get();
//
//        boolean loincOnly = true;
//        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("lab_count_loinc_only.csv", false), StandardCharsets.UTF_8))) {
//            itemCounts.entrySet().stream().sorted((e1, e2) -> e2.getValue() - e1.getValue())
//                    .forEachOrdered(e -> {
//                        String loinc = itemLoincMap.get(e.getKey());
//                        int count = e.getValue().intValue();
//                        try {
//                            if (loincOnly && (loinc != null)) {
//                                //writer.write(String.format("%s,%d", loinc, e.getValue()));
//                                writer.write(loinc);
//                                writer.write(",");
//                                writer.write(String.valueOf(count));
//                                writer.write(",");
//                                writer.write(Double.toString(100.0 * e.getValue() / TOTAL_LABS));
//                                writer.write("\n");
//                            }
//                            if (!loincOnly) {
//                                writer.write(loinc == null ? "unknown" : loinc);
//                                writer.write(",");
//                                writer.write(e.getValue());
//                                writer.write(",");
//                                writer.write(Double.toString(100.0 * e.getValue() / TOTAL_LABS));
//                            }
////                            writer.write(loinc + "," + count);
////                            writer.write("\n");
//
//
//                        } catch (IOException exception){
//                            exception.printStackTrace();
//                        }
//
//                    });
//
//        } catch (FileNotFoundException e){
//            e.printStackTrace();
//        } catch (IOException e){
//            e.printStackTrace();
//        }


        units.values().stream().filter(lab -> lab.countByUnit.size() > 1)
                .filter(lab -> { // max count not dominanted by one unit
                    List<Integer> counts = new ArrayList<>(lab.getCountByUnit().values());
                    Collections.sort(counts);
                    Collections.reverse(counts);
                    int total = counts.stream().reduce((x, y) -> x + y).get();
                    return ((double)counts.get(0) / total) < 0.8;
                })
                .forEach(System.out::println);



    }

    static class Lab {
        String id; //lab test id, could be a LOINC code
        Map<String, Double> meanByUnit;
        Map<String, Integer> countByUnit;

        public Lab(String id){
            this.id = id;
            this.meanByUnit = new HashMap<>();
            this.countByUnit = new HashMap<>();
        }

        public void add(String unit, Double value){
            this.countByUnit.putIfAbsent(unit, 0);
            this.meanByUnit.putIfAbsent(unit, 0.0);
            int n = this.countByUnit.get(unit);
            double mean = this.meanByUnit.get(unit);
            double updated_mean = (mean * n + value) / (n + 1);
            this.meanByUnit.put(unit, updated_mean);
            this.countByUnit.put(unit, n + 1);
        }

        public String getId() {
            return id;
        }

        public Map<String, Double> getMeanByUnit() {
            return new HashMap<>(meanByUnit);
        }

        public Map<String, Integer> getCountByUnit() {
//            return countByUnit.entrySet().stream()
//                    .sorted((e1, e2) -> e2.getValue() - e1.getValue())
//                    .collect(Collectors.toMap(e -> e.getKey(), e -> e.getValue()));
            return new HashMap<>(this.countByUnit);
        }

        @Override
        public String toString() {
            StringBuilder builder = new StringBuilder();
            builder.append("id: " + id);
            builder.append("; ");
            for (String unit : this.countByUnit.keySet()) {
                builder.append(unit);
                builder.append("--");
                builder.append("count: " + this.countByUnit.get(unit));
                builder.append(" ; mean: ");
                builder.append(this.meanByUnit.get(unit));
                builder.append(" ");
            }
            return builder.toString();
        }

    }
}
