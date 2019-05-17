package org.jax.service;

import org.jax.Entity.LabEvents;
import org.jax.dao.LabRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class LabItemServiceDbImpl implements LabItemService {

    @Autowired
    LabRepository labRepository;

    @Override
    public Optional<LabEvents> findById(int id) {

        return labRepository.findById(id);

    }
}
