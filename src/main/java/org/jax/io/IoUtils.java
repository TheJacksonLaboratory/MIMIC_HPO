package org.jax.io;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;

public class IoUtils {

    private static final Logger logger = LoggerFactory.getLogger(IoUtils.class);

    public static BufferedWriter getWriter(String path){
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(System.out));
        try {
            writer = new BufferedWriter(new FileWriter(path));
        } catch (Exception e) {
            logger.info("Cannot create writer for file: " + path);
            logger.info("Writing to console...");
        }

        return new BufferedWriter(writer);
    }

}
