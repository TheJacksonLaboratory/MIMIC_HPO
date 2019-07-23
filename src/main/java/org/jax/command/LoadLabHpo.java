package org.jax.command;

import com.beust.jcommander.Parameter;
import org.jax.Entity.LabHpo;
import org.jax.service.LabHpoService;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

public class LoadLabHpo implements MimicCommand {

    @Parameter(names = {"-hpo_lab", "--hpo_from_lab"}, description = "specify hpo file mapped from LOINC lab")
    private String lab2hpoPath;

    @Autowired //todo: figure out how to inject it
    LabHpoService service;

    @Override
    public void run() {
        try (BufferedReader reader = new BufferedReader(new FileReader(lab2hpoPath))){
            String line;
            int count = 0;
            while ((line = reader.readLine()) != null){
                if (!line.startsWith("ROW_ID")){ //ignore header
                    String [] elems = line.split(",");
                    int rowId = Integer.parseInt(elems[0]);
                    String negated = elems[1];
                    String map_to = elems[2];
                    LabHpo labHpo = new LabHpo(rowId, negated, map_to);
                    //System.out.println(labHpo);
                    //service.save(labHpo);
                    count++;
                }
            }
            System.out.println("total lines: " + count);
            System.out.println("service is null: " + (service == null));
        } catch (FileNotFoundException e){
            e.printStackTrace();
        } catch (IOException e){
            e.printStackTrace();
        }
    }
}
