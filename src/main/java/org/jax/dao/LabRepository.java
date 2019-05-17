package org.jax.dao;

import org.jax.Entity.LabEvents;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LabRepository extends JpaRepository<LabEvents, Integer> { }
