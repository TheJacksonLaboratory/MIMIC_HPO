package org.jax.service;

import org.monarchinitiative.phenol.io.OntologyLoader;
import org.monarchinitiative.phenol.ontology.algo.OntologyAlgorithm;
import org.monarchinitiative.phenol.ontology.data.Ontology;
import org.monarchinitiative.phenol.ontology.data.TermId;

import javax.annotation.PostConstruct;
import java.io.File;
import java.util.Set;

/**
 * Hpo related service
 */
public class HpoService {

    private String hpoOboPath;
    private Ontology ontology;

    public HpoService(){}

    public HpoService(String hpoOboPath){
        this.hpoOboPath = hpoOboPath;
    }

    public void setHpoOboPath(String hpoOboPath){
        this.hpoOboPath = hpoOboPath;
    }

    //@PostConstruct
    public void init(){
        this.ontology = OntologyLoader.loadOntology(new File(this.hpoOboPath));
    }

    public Ontology hpo(){
        return this.ontology;
    }

    public Set<TermId> infer(TermId id, boolean includeSelf){
        return OntologyAlgorithm.getAncestorTerms(this.ontology, id, includeSelf);
    }

}
