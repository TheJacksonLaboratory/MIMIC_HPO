package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.service.HpoService;
import org.jax.service.InferLabHpoService;
import org.jax.service.InferNoteHpoService;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * Infer additional terms based on HPO hierarchy, and write the inferred HPO into a separate table.
 */
@Parameters(commandDescription = "Infer parent HPO terms based on abnormalities indicated by children terms")
public class HpoInferenceCmd implements MimicCommand {

    @Parameter(names = {"-hpo", "--hpo_path"}, description = "specify the path to hp.obo")
    private String hpoPath;

    @Parameter(names = {"-table", "--table"}, description = "infer LabHpo or NoteHpo", required = true)
    private String table;

    @Autowired
    HpoService hpoService;

    @Autowired
    InferLabHpoService inferLabHpoService;

    @Autowired
    InferNoteHpoService inferNoteHpoService;

    @Override
    public void run() {
        //TODO: how to inject hpoPath to hpoService and let it init automatically. Alternatively, we probably should package hp.obo and loinc2hpoAnnotation.txt in our software or add a url download function. It would be easier to control versions and simplify the use.
        hpoService.setHpoOboPath(hpoPath);
        hpoService.init();

        switch (table) {
            case "LabHpo":
                inferLabHpoService.initTable();
                inferLabHpoService.infer(1000);
                inferLabHpoService.createIndexOnForeignKey();
                break;
            case "NoteHpo":
                inferNoteHpoService.initTable();
                inferNoteHpoService.infer(1000);
                //inferNoteHpoService.createIndexOnForeignKey();
                break;
            default:
                System.err.println("Unable to recognize " + table);
        }


    }
}
