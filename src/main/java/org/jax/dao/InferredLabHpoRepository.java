package org.jax.dao;

import org.jax.Entity.InferredLabHpo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface InferredLabHpoRepository extends JpaRepository<InferredLabHpo, Integer>{
}
