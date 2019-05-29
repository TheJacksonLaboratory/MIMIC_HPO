package org.jax.lab2hpo;

/**
 * Used to indicate that the unit is not recognized in {@link LabSummary}
 */
public class UnrecognizedUnitException extends Exception {
    public UnrecognizedUnitException () {
        super();
    }

    public UnrecognizedUnitException(String message) {
        super(message);
    }
}
