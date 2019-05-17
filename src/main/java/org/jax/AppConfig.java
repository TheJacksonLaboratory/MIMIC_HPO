package org.jax;

import org.jax.service.LabItemService;
import org.jax.service.LabItemServiceDbImpl;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    LabItemService labItemService() {
        return new LabItemServiceDbImpl();
    }

}
