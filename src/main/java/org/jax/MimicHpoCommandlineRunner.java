package org.jax;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.ParameterException;
import org.jax.command.HpoInferenceCmd;
import org.jax.command.LabToHpoCmd;
import org.jax.command.MimicCommand;
import org.jax.command.SummarizeLabCmd;
import org.springframework.boot.CommandLineRunner;

public class MimicHpoCommandlineRunner implements CommandLineRunner {

    @Override
    public void run(String[] args) {
        long startTime = System.currentTimeMillis();

        MimicCommand summarizeLab = new SummarizeLabCmd();
        MimicCommand labToHpo = new LabToHpoCmd();
        MimicCommand hpoInference = new HpoInferenceCmd();

        JCommander jc = JCommander.newBuilder()
                .addObject(this)
                .addCommand("summarizeLab", summarizeLab)
                .addCommand("lab2hpo", labToHpo)
                .addCommand("hpoInference", hpoInference)
                .build();
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
            default:
                    System.err.println(String.format("[ERROR] command \"%s\" not recognized",command));
                    jc.usage();
                    System.exit(1);
        }

        mimicCommand.run();

        long stopTime = System.currentTimeMillis();
        System.out.println("Phenomiser: Elapsed time was " + (stopTime - startTime)*(1.0)/1000 + " seconds.");

    }

}
