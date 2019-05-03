package org.jax;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

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
                String[] elements = line.split("[\\,]");
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
                if (count % 10000 == 0) {
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
                String[] elements = line.split("[,]");
                
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    public static void main( String[] args ) {

        String lab_path = "/Users/zhangx/git/MIMIC_HPO/src/main/resources/LABEVENTS.csv";
        Map<String, Integer> itemCounts = labItemCounts(lab_path);
        itemCounts.entrySet().stream().sorted((e1, e2) -> e2.getValue() - e1.getValue()).limit(10).forEachOrdered(e -> {
            System.out.println(e.getKey() + ": " + e.getValue());
        });



    }
}
