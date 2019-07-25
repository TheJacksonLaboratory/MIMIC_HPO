package org.jax;

import org.jax.command.HpoInferenceCmd;
import org.jax.command.LabToHpoCmd;
import org.jax.command.MimicCommand;
import org.jax.command.SummarizeLabCmd;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {
	
    @Bean (name = "summarizeLab")
    MimicCommand summarizeLab(){
        return new SummarizeLabCmd();
    }

    @Bean (name = "labToHpo")
    MimicCommand labToHpo() {
        return new LabToHpoCmd();
    }

    @Bean (name = "hpoInference")
    MimicCommand hpoInference(){
        return new HpoInferenceCmd();
    }
}
