package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

/**
 * Class to convert laboratory tests into HPO terms
 */
@Parameters(commandDescription = "Convert Lab tests into Hpo")
public class LabToHpoCmd implements MimicCommand {
    @Parameter(names = {"-o", "--output"}, description = "Output path")
    private String outPath;
    @Override
    public void run() {
        //How to?
        //input: lab record + summary file (obtain through running SummarizeLabCmd command)
        //for each lab record,
        //  read the "unit" filed, discard if it is an outlier, unless it is one the three special cases
        //
        //read the "flag" and "value" fields, and create a more meaningful "flag":
        //  if the "value" is not a number, keep the "flag" unchanged
        //  if the "value" is a number and the "flag" is abnormal, compare "value" with mean: assign "H" if value > mean, "L" otherwise.
        System.out.println("Lab to HPO -> " + outPath);

    }
}
