package org.jax;

import org.jax.command.HpoInferenceCmd;
import org.jax.command.LabToHpoCmd;
import org.jax.command.LoadLabHpo;
import org.jax.command.MimicCommand;
import org.jax.command.SummarizeLabCmd;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {
	
	@Autowired
	LabSummaryService labSummaryService;

    @Bean (name = "summarizeLab")
    MimicCommand summarizeLab(){
        return new SummarizeLabCmd(labSummaryService);
    }

    @Bean (name = "labToHpo")
    MimicCommand labToHpo() {
        return new LabToHpoCmd();
    }

    @Bean (name = "loadLabHpo")
    MimicCommand loadLabHpo() {
        return new LoadLabHpo();
    }

    @Bean (name = "hpoInference")
    MimicCommand hpoInference(){
        return new HpoInferenceCmd();
    }

}
