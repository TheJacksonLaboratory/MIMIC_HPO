package org.jax.service;

import org.jax.Entity.LabHpo;
import org.jax.dao.LabHPORepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class LabHpoService {

    @Autowired
    LabHPORepository labHPORepository;

    public void save(LabHpo labHpo){
        labHPORepository.save(labHpo);
    }

}
