package org.jax.service;

import java.util.Optional;

public interface LabDictService {

    Optional<String> loincOf(int id);

}
