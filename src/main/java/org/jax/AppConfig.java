package org.jax;

import org.jax.command.*;
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

    @Bean (name = "textToHpo")
    MimicCommand textToHpo(){
        return new TextToHpoCmd();
    }

}
