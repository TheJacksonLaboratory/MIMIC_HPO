package org.jax;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.ParameterException;
import org.jax.command.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class MimicHpoCommandlineRunner implements CommandLineRunner {

    @Autowired @Qualifier("summarizeLab")
    MimicCommand summarizeLab;
    @Autowired @Qualifier("labToHpo")
    MimicCommand labToHpo;
    @Autowired @Qualifier ("hpoInference")
    MimicCommand hpoInference;
    @Autowired @Qualifier ("loadLabHpo")
    MimicCommand loadLabHpo;

    @Autowired JCommander jc;

    @Override
    public void run(String[] args) {
        long startTime = System.currentTimeMillis();

//        MimicCommand summarizeLab = new SummarizeLabCmd();
//        MimicCommand labToHpo = new LabToHpoCmd();
//        MimicCommand hpoInference = new HpoInferenceCmd();
//        MimicCommand loadLabHpo = new LoadLabHpo();

//        JCommander jc = JCommander.newBuilder()
//                .addObject(this)
//                .addCommand("summarizeLab", summarizeLab)
//                .addCommand("lab2hpo", labToHpo)
//                .addCommand("hpoInference", hpoInference)
//                .addCommand("loadLabHpo", loadLabHpo)
//                .build();
        jc.addObject(this);
        try {
            jc.parse(args);
        } catch (ParameterException e) {
            for (String arg : args) {
                if (arg.contains("h")) {
                    jc.usage();
                    System.exit(0);
                }
            }
            e.printStackTrace();
            jc.usage();
            System.exit(1);
        }

        String command = jc.getParsedCommand();

        if (command == null) {
            jc.usage();
            System.exit(1);
        }

        MimicCommand mimicCommand = null;

        switch (command) {
            case "summarizeLab":
                mimicCommand = summarizeLab;
                break;
            case "lab2hpo":
                mimicCommand = labToHpo;
                break;
            case "hpoInference":
                mimicCommand = hpoInference;
                break;
            case "loadLabHpo":
                mimicCommand = loadLabHpo;
                break;
            default:
                    System.err.println(String.format("[ERROR] command \"%s\" not recognized",command));
                    jc.usage();
                    System.exit(1);
        }

        mimicCommand.run();

        long stopTime = System.currentTimeMillis();
        System.out.println("Mimic2Hpo: Elapsed time was " + (stopTime - startTime)*(1.0)/1000 + " seconds.");

    }

}
