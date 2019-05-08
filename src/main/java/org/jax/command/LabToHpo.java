package org.jax.command;

/**
 * Class to convert laboratory tests into HPO terms
 */
public class LabToHpo implements MimicCommand {
    @Override
    public void run() {
        //How to?
        //input: lab record + summary file (obtain through running SummarizeLab command)
        //for each lab record,
        //  read the "unit" filed, discard if it is an outlier, unless it is one the three special cases
        //
        //read the "flag" and "value" fields, and create a more meaningful "flag":
        //  if the "value" is not a number, keep the "flag" unchanged
        //  if the "value" is a number and the "flag" is abnormal, compare "value" with mean: assign "H" if value > mean, "L" otherwise.

    }
}
