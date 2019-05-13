package org.jax.service;


import org.jax.Entity.LabEvents;

import java.util.List;

/**
 * Service queries of lab items
 */
public interface LabItemService {

    List<LabEvents> findById(int id);

}
