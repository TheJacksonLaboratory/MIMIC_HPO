package org.jax.io;

import org.jax.lab2hpo.LabSummary;

import java.util.Map;

public interface QnLabSummarize {
    Map<Integer, LabSummary> summarize() throws Exception;
}
