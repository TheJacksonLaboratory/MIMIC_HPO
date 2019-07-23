package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.service.HpoService;
import org.jax.service.InferLabHpoService;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * Infer additional terms based on HPO hierarchy
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

        hpoService.setHpoOboPath(hpoPath);
        hpoService.init();

        System.out.println("hpoService is null: " + (hpoService==null));
        System.out.println("number of terms: " + hpoService.hpo().getTermMap().size());

        System.out.println("inferLabHpoService is null: " + (inferLabHpoService ==null));

        int[] id_range = inferLabHpoService.id_range();
        System.out.println(String.format("min = %d; max = %d", id_range[0], id_range[1]));
        inferLabHpoService.initTable();
        inferLabHpoService.infer();
    }
}
