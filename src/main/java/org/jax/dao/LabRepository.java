package org.jax.dao;

import org.jax.Entity.LabEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LabRepository extends JpaRepository<LabEvent, Integer> { }
