package org.jax.lab2hpo;

import java.util.Map;
import java.util.Optional;

import org.hl7.fhir.dstu3.model.Coding;
import org.jax.Entity.JHULab;
import org.jax.service.LocalLabTestNotMappedToLoinc;
import org.monarchinitiative.loinc2hpo.codesystems.Code;
import org.monarchinitiative.loinc2hpo.exception.LoincCodeNotAnnotatedException;
import org.monarchinitiative.loinc2hpo.exception.MalformedLoincCodeException;
import org.monarchinitiative.loinc2hpo.exception.UnrecognizedCodeException;
import org.monarchinitiative.loinc2hpo.loinc.HpoTerm4TestOutcome;
import org.monarchinitiative.loinc2hpo.loinc.LOINC2HpoAnnotationImpl;
import org.monarchinitiative.loinc2hpo.loinc.LoincId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Class that does the heavy lifting in this project: convert a lab into HPO.
 */
public class JHULabView2HpoFactory {

    private static final Logger logger = LoggerFactory.getLogger(JHULabView2HpoFactory.class);

    // Loinc2Hpo annotations
    private Map<LoincId, LOINC2HpoAnnotationImpl> annotationMap;


    public JHULabView2HpoFactory(Map<LoincId, LOINC2HpoAnnotationImpl> annotationMap) {
        this.annotationMap = annotationMap;
    }

    public Optional<HpoTerm4TestOutcome> convert(JHULab lab) throws LocalLabTestNotMappedToLoinc, MalformedLoincCodeException, LoincCodeNotAnnotatedException, UnrecognizedUnitException, UnableToInterpretateException, UnrecognizedCodeException {


        String loinc = lab.getLoinc_id();
        
        //throws MalformedLoincCodeException
        LoincId loincId = new LoincId(loinc);

        //check whether the loinc is annotated
        if (!annotationMap.containsKey(loincId)) {
            throw new LoincCodeNotAnnotatedException();
        }
        
        Float value = lab.getResult_num();
        Float low = Float.parseFloat(lab.getRange_low());
        Float high = Float.parseFloat(lab.getRange_high());
        
        // placeholder of interpretation code
        String code = null;

        if (value < low) {
        	code = "L";
        } else if (value > high) {
        	code = "H";
        } else {
        	code = "N";
        }

        Code interpretation = new Code(new Coding().setSystem("FHIR").setCode(code));
        LOINC2HpoAnnotationImpl annotation = annotationMap.get(loincId);
        if (annotation.getCandidateHpoTerms().containsKey(interpretation)) {
            return Optional.of(annotation.getCandidateHpoTerms().get(interpretation));
        } else {
            throw new UnrecognizedCodeException("Interpretation code is not mapped to hpo");
        }

    }

}
