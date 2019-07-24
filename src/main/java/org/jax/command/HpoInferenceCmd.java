package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.service.HpoService;
import org.jax.service.InferLabHpoService;
import org.springframework.beans.factory.annotation.Autowired;

import java.sql.SQLException;

/**
 * Infer additional terms based on HPO hierarchy, and write the inferred HPO into a separate table.
 */
@Parameters(commandDescription = "Infer parent HPO terms based on abnormalities indicated by children terms")
public class HpoInferenceCmd implements MimicCommand {

    @Parameter(names = {"-hpo", "--hpo_path"}, description = "specify the path to hp.obo")
    private String hpoPath;

    @Autowired
    HpoService hpoService;

    @Autowired
    InferLabHpoService inferLabHpoService;

    @Override
    public void run() {

        System.out.println(hpoPath);

        //TODO: how to inject hpoPath to hpoService and let it init automatically. Alternatively, we probably should package hp.obo and loinc2hpoAnnotation.txt in our software or add a url download function. It would be easier to control versions and simplify the use.
        hpoService.setHpoOboPath(hpoPath);
        hpoService.init();

        inferLabHpoService.initTable();
        try {
            inferLabHpoService.infer();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
