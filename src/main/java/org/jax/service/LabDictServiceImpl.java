package org.jax.service;

import org.jax.Entity.LabDictItem;

import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Serve lookup from local lab test item_id to LOINC
 */
public class LabDictServiceImpl implements LabDictService {

    private Map<Integer, String> itemIdToLoinc;

    public LabDictServiceImpl(Map<Integer, LabDictItem> labDictItemMap) {

        this.itemIdToLoinc = labDictItemMap.values().stream()
                .collect(Collectors.toMap(item -> item.getItemId(), item -> item.getLoincCode(),
                        (a, b) -> a));
    }

    @Override
    public Optional<String> loincOf(int id) {
        return Optional.of(this.itemIdToLoinc.get(id));
    }
}
