package org.jax.io;


import org.jax.Entity.LabDictItem;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;


public class LabDictParserTest {

    static Map<Integer, LabDictItem> labDictItemMap;

    @BeforeAll
    public static void setUp() throws Exception {
        String path = LabDictParserTest.class.getClassLoader().getResource("D_LABITEMS_test.csv").getPath();
        LabDictParser parser = new LabDictParser(path);
        labDictItemMap = parser.parse();

    }


    @ParameterizedTest (name = "test D_LABOTEMS.csv parser")
    @CsvSource(value = {
            "255|51055|'Lipase, Pleural'|'Pleural'|'Chemistry'|''",
            "595|51395|'CD15'|'Other Body Fluid'|'Hematology'|'51252-5'",
            "163|50962|'N-Acetylprocainamide (NAPA)'|'Blood'|'Chemistry'|'3834-9'"
    }, delimiter = '|')
    public void getLabDict(int row_id, int item_id, String label, String fluid, String category, String loinc_code) throws Exception {
        System.out.println(labDictItemMap.get(row_id).getLabel());
        assertEquals(labDictItemMap.get(row_id).getItemId(), item_id);
        assertEquals(labDictItemMap.get(row_id).getLabel(), label);
        assertEquals(labDictItemMap.get(row_id).getFluid(), fluid);
        assertEquals(labDictItemMap.get(row_id).getCategory(), category);
        assertEquals(labDictItemMap.get(row_id).getLoincCode(), loinc_code);

    }

}