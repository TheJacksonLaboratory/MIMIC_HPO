package org.jax.service;


import org.jax.Entity.LabEvent;

import java.util.Optional;

/**
 * Service queries of lab items
 */
public interface LabItemService {

    Optional<LabEvent> findById(int id);

}
