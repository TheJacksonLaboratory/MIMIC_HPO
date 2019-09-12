package org.jax.io;

import org.jax.Entity.LabDictItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * This class parses the D_LABITEMS.csv file and provide a map from primary key to all records.
 * NoteEvent: the primary key is row_id, not lab item_id
 */
public class LabDictParser {

    private static final Logger logger = LoggerFactory.getLogger(LabDictParser.class);

    private String path;
    private Map<Integer, LabDictItem> labDict;

    public LabDictParser(String path) {
        this.path = path;
    }


    /**
     * Primary key (row_id) to record mapping. NoteEvent: row_id is the primary key for this table; lab item identification uses "item_id".
     * @return
     * @throws IOException
     */
    public Map<Integer, LabDictItem> parse() throws IOException {

        Map<Integer, LabDictItem> itemToLoincMap = new HashMap<>();
        BufferedReader reader = new BufferedReader(new FileReader(path));
        String line = reader.readLine();
        while ((line = reader.readLine()) != null) {
            if (line.endsWith(",")) {
                line = line + " ";
            }
            String[] elements = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)");
            if (elements.length != 6){
                System.out.println("line does not have 6 fields: " + line);
            }

            try{
                int rowid = Integer.valueOf(elements[0]);
                int itemId = Integer.valueOf(elements[1]);
                String label = elements[2].replace("\"", "").trim();
                String fluid = elements[3].replace("\"", "").trim();
                String category = elements[4].replace("\"", "").trim();
                String loinc = elements[5].replace("\"", "").trim();

                LabDictItem labDictItem = new LabDictItem(rowid, itemId, label, fluid, category, loinc);

                itemToLoincMap.put(rowid, labDictItem);
            } catch (Exception e){
                logger.warn("String to int conversion error (line skipped): " + line);
            }
        }

        return itemToLoincMap;

    }

}
