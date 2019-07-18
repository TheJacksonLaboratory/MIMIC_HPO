package org.jax.io;

import org.jax.lab2hpo.LabSummary;

import java.util.Map;


/**
 * This class access the dababase, and calculate summary statistics for Qn lab tests.
 * @TODO: implement this class with the SQL query {@link resources/sql/analysis.sql}. Output a table {@link resources/lab_summary.tsv}
 */
public class QnLabSummarizeDbImpl implements QnLabSummarize {

    @Override
    public Map<Integer, LabSummary> summarize() throws Exception {
        return null;
    }
}
