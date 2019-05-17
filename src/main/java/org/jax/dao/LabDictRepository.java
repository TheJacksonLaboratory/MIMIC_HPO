package org.jax.dao;

import org.jax.Entity.LabDictItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LabDictRepository extends JpaRepository<LabDictItem, Integer> {
}
