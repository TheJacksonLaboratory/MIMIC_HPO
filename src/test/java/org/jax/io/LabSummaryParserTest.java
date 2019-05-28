package org.jax.io;

import org.jax.LabSummary;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class LabSummaryParserTest {

    private static Map<Integer, LabSummary> labSummaryMap;

    @BeforeAll
    private static void setup() throws Exception{
        String path = LabSummaryParserTest.class.getClassLoader().getResource("lab_summary_test.tsv").getPath();
        LabSummaryParser labSummaryParser = new LabSummaryParser(path);
        labSummaryMap = labSummaryParser.parse();
    }

    @Test
    void parse() {
        assertNotNull(labSummaryMap);
    }

    @ParameterizedTest
    @CsvSource(value = {
            "51221, 2",
            "51274, 3",
            "51237, 1",
            "51019, 1"
    })
    void numUnits(int id, int numUnits) {
        assertEquals(labSummaryMap.get(id).getCountByUnit().size(), numUnits);
    }

    @ParameterizedTest
    @CsvSource(value = {
            "51221, %, 31.219442208350724",
            "51279, NULL, 3.390000025431315",
            "51019, g/dL, 2.700000047683716"
    })
    void mean(int id, String unit, double mean){
        assertEquals(labSummaryMap.get(id).getMeanByUnit().get(unit), mean, 0.0001);
    }

    @Test
    void range() {
        assertNull(labSummaryMap.get(51221).getNormalRangeByUnit().get("NULL"));
    }

}