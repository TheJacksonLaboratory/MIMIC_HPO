package org.jax;

import com.beust.jcommander.JCommander;
import org.jax.command.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

//    @Bean
//    JCommander jcommander(MimicCommand summarizeLab, MimicCommand labToHpo, MimicCommand loadLabHpo,
//                          MimicCommand hpoInference) {
//        JCommander jc = JCommander.newBuilder()
//                //.addObject(this)
//                .addCommand("summarizeLab", summarizeLab)
//                .addCommand("lab2hpo", labToHpo)
//                .addCommand("hpoInference", hpoInference)
//                .addCommand("loadLabHpo", loadLabHpo)
//                .build();
//        return jc;
//    }

    @Bean (name = "summarizeLab")
    MimicCommand summarizeLab(){
        return new SummarizeLabCmd();
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
