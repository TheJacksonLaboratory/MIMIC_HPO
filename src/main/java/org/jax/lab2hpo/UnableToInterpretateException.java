package org.jax.lab2hpo;

/**
 * Exception to indicate that a lab result cannot be interpret
 */
public class UnableToInterpretateException extends Exception {

    public UnableToInterpretateException() {
        super();
    }

    public UnableToInterpretateException(String message) {
        super(message);
    }
}
