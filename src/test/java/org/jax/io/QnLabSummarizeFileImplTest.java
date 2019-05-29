package org.jax.io;

import org.jax.lab2hpo.LabSummary;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class QnLabSummarizeFileImplTest {

    static Map<Integer, LabSummary> summaryMap;

    @BeforeAll
    static void setUp() throws Exception {

        String labEventPath = QnLabSummarizeFileImplTest.class.getClassLoader().getResource("LABEVENTS_test.tsv").getPath();
        QnLabSummarize qnLabSummarize = new QnLabSummarizeFileImpl(labEventPath);
        summaryMap = qnLabSummarize.summarize();

    }

    @ParameterizedTest
    @CsvSource({
            "50878, 1",
            "50868, 1",
            "51279, 2"
    })
    void unitsPerTest(int itemId, int count) {

        assertEquals(summaryMap.get(itemId).getMeanByUnit().size(), count);

    }

    @ParameterizedTest
    @CsvSource(value = {
            "50878, 'IU/L', 1",
            "50868, 'mEq/L', 2",
            "51279, 'm/uL', 3",
            "51279, 'g/mL', 1"
    })
    void countPerTest(int itemId, String unit, int count) {

        assertEquals(summaryMap.get(itemId).getCountByUnit().get(unit.toLowerCase()).intValue(), count);

    }

    @ParameterizedTest
    @CsvSource(value = {
            "50878, 'IU/L', 31",
            "50868, 'mEq/L', 11.5",
            "51279, 'm/uL', 3.30333333",
            "51279, 'g/mL', 4.04"
    })
    void meanPerTest(int itemId, String unit, double mean) {

        assertEquals(summaryMap.get(itemId).getMeanByUnit().get(unit.toLowerCase()), mean, 0.0001);

    }

}