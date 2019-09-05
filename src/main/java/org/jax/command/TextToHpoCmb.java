package org.jax.command;

import com.beust.jcommander.Parameters;
import org.jax.text2hpo.MimicRadiology2Hpo;
import org.springframework.beans.factory.annotation.Autowired;

@Parameters(commandDescription = "convert notes into HPO")
public class TextToHpoCmb implements MimicCommand {

    @Autowired
    MimicRadiology2Hpo mimicRadiology2Hpo;

    @Override
    public void run() {
        System.out.println("run notes to hpo");
        mimicRadiology2Hpo.note2hpo();
    }
}
