package org.jax;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;



/**
 * Hello world!
 *
 */
@SpringBootApplication
public class MimicHpoSpringApp {

    public static void main( String[] args ) {

        SpringApplication.run(MimicHpoCommandlineRunner.class, args);



//        String lab_path = "/Users/zhangx/git/MIMIC_HPO/src/main/resources/LABEVENTS.csv";
//        String lab_items_path = "/Users/zhangx/git/MIMIC_HPO/src/main/resources/D_LABITEMS.csv";
//        Map<String, Integer> itemCounts = labItemCounts(lab_path);
//        Map<String, String> itemLoincMap = itemToLoinc(lab_items_path);
//        Map<String, LabSummary> units = summarize(lab_path);

//        int TOTAL_LABS = itemCounts.values().stream().reduce((e1, e2) -> e1 + e2).get();
//
//        boolean loincOnly = true;
//        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("lab_count_loinc_only.csv", false), StandardCharsets.UTF_8))) {
//            itemCounts.entrySet().stream().sorted((e1, e2) -> e2.getValue() - e1.getValue())
//                    .forEachOrdered(e -> {
//                        String loincOf = itemLoincMap.get(e.getKey());
//                        int count = e.getValue().intValue();
//                        try {
//                            if (loincOnly && (loincOf != null)) {
//                                //writer.write(String.format("%s,%d", loincOf, e.getValue()));
//                                writer.write(loincOf);
//                                writer.write(",");
//                                writer.write(String.valueOf(count));
//                                writer.write(",");
//                                writer.write(Double.toString(100.0 * e.getValue() / TOTAL_LABS));
//                                writer.write("\n");
//                            }
//                            if (!loincOnly) {
//                                writer.write(loincOf == null ? "unknown" : loincOf);
//                                writer.write(",");
//                                writer.write(e.getValue());
//                                writer.write(",");
//                                writer.write(Double.toString(100.0 * e.getValue() / TOTAL_LABS));
//                            }
////                            writer.write(loincOf + "," + count);
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


//        units.values().stream().filter(lab -> lab.countByUnit.size() > 1)
//                .filter(lab -> { // max count not dominanted by one unit
//                    List<Integer> counts = new ArrayList<>(lab.getCountByUnit().values());
//                    Collections.sort(counts);
//                    Collections.reverse(counts);
//                    int total = counts.stream().reduce((x, y) -> x + y).get();
//                    return ((double)counts.get(0) / total) < 0.8;
//                })
//                .forEach(System.out::println);



    }






}
