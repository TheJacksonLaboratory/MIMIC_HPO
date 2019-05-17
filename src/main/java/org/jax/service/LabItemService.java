package org.jax.service;


import org.jax.Entity.LabEvents;

import java.util.List;
import java.util.Optional;

/**
 * Service queries of lab items
 */
public interface LabItemService {

    Optional<LabEvents> findById(int id);

}
