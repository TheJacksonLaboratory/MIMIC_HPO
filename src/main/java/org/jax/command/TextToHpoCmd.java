package org.jax.command;

import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import org.jax.text2hpo.MimicRadiology2Hpo;
import org.springframework.beans.factory.annotation.Autowired;

@Parameters(commandDescription = "convert notes into HPO")
public class TextToHpoCmd implements MimicCommand {

    @Autowired
    MimicRadiology2Hpo mimicRadiology2Hpo;

    @Parameter(names = {"-i", "--input"})
    private String input;

    @Override
    public void run() {
        System.out.println("run notes to hpo");
        // The following code works. It can use either MetaMap Web API or the Java API for locally hosted Metamap. On average, it takes about 6 seconds to process one report using the web API and 2 seconds if locally hosted.
        // It would take the web API 35 days to process half million radiology reports from MIMIC, and one third of that time if the MetaMap is locally hosted. Processing notes in batches does not increase speed. It will multiply the time by batch size. Unless the MetaMap itself supports concurrency, there is little benefit to send concurrent queries.
//        mimicRadiology2Hpo.note2hpo(10);

        // Instead, we used ClinPhen command line app to extract HPO.
        // Note: The original source code has some issues with Python3.
        // If running on a laptop, it will take > 8 hours; on a cluster with 32 CPUs, it takes 4 hours.
        // For MIMIC data, go to JAX helix to find the script.
        mimicRadiology2Hpo.importClinPhenResult(input);
    }
}
