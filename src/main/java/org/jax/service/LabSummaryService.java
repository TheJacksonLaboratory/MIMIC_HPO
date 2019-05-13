package org.jax.service;

import java.util.Map;

/**
 * Services related to lab summary statistics
 */
public interface LabSummaryService {

    Map<Integer, String> primaryUnit();

    Map<Integer, Double> meanOfPrimaryUnit();

}
