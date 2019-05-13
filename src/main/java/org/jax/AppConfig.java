package org.jax;

import org.jax.dao.LabRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Autowired
    public LabRepository labRepository;

}
