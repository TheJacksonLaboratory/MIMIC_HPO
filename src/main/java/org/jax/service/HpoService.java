package org.jax.service;

import java.io.File;
import java.util.HashSet;
import java.util.Set;

import org.monarchinitiative.phenol.io.OntologyLoader;
import org.monarchinitiative.phenol.ontology.algo.OntologyAlgorithm;
import org.monarchinitiative.phenol.ontology.data.Ontology;
import org.monarchinitiative.phenol.ontology.data.TermId;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;

/**
 * Hpo related service
 */
@Service
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

    @PostConstruct
    public void init(){

        if (this.hpoOboPath != null) {
            this.ontology = OntologyLoader.loadOntology(new File(this.hpoOboPath));
        }

    }

    public Ontology hpo(){
        return this.ontology;
    }

    public Set<TermId> infer(TermId id, boolean includeSelf){
        // id could be non-primary id
        TermId primary = this.ontology.getPrimaryTermId(id);

        return OntologyAlgorithm.getAncestorTerms(this.ontology, primary, includeSelf);
    }

}
