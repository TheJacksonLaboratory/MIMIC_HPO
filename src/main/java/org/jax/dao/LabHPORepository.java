package org.jax.dao;

import org.jax.Entity.LabHpo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LabHPORepository extends JpaRepository<LabHpo, Integer>{
}
