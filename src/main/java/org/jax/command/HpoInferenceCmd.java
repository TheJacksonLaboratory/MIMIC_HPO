package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

/**
 * Infer additional terms based on HPO hierarchy
 */
@Parameters(commandDescription = "Infer parent HPO terms based on abnormalities indicated by children terms")
public class HpoInferenceCmd implements MimicCommand {

    @Parameter(names = {"-hpo", "--hpo_path"}, description = "specify the path to hp.obo")
    private String hpoPath;

    @Override
    public void run() {

        System.out.println(hpoPath);

    }
}
