package org.jax.service;

import org.hl7.fhir.dstu3.model.Coding;
import org.jax.Entity.LabEvents;
import org.monarchinitiative.loinc2hpo.codesystems.Code;
import org.monarchinitiative.loinc2hpo.exception.MalformedLoincCodeException;
import org.monarchinitiative.loinc2hpo.loinc.HpoTerm4TestOutcome;
import org.monarchinitiative.loinc2hpo.loinc.LOINC2HpoAnnotationImpl;
import org.monarchinitiative.loinc2hpo.loinc.LoincEntry;
import org.monarchinitiative.loinc2hpo.loinc.LoincId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Optional;

/**
 * Class that does the heavy lifting in this project: convert a labevent into HPO.
 */
public class LabEvents2HpoFactory {

    private static final Logger logger = LoggerFactory.getLogger(LabEvents2HpoFactory.class);

    // local lab test codes to LOINC mapping
    private Map<Integer, String> local2LoincMap;
    // primary units for each lab test
    // obtained from LabSummaryParser
    private Map<Integer, String> primaryUnits;
    // mean value for quantitative lab tests, key is the primary unit
    // obtained from LabSummaryParser
    private Map<Integer, Double> primaryMeans;
    // Loinc2Hpo annotations
    private Map<LoincId, LOINC2HpoAnnotationImpl> annotationMap;
    // Loinc entry
    private Map<LoincId, LoincEntry> loincEntryMap;

    public LabEvents2HpoFactory(Map<Integer, String> local2LoincMap,
                                Map<Integer, String> primaryUnits,
                                Map<Integer, Double> primaryMeans,
                                Map<LoincId, LOINC2HpoAnnotationImpl> annotationMap,
                                Map<LoincId, LoincEntry> loincEntryMap){
        this.local2LoincMap = local2LoincMap;
        this.primaryUnits = primaryUnits;
        this.primaryMeans = primaryMeans;
        this.annotationMap = annotationMap;
        this.loincEntryMap = loincEntryMap;
    }

    public Optional<HpoTerm4TestOutcome> convert(LabEvents labEvents) throws MalformedLoincCodeException {

        LoincId loincId = null;

        // This could throw a MalformedLoincCodeException
        loincId = new LoincId(local2LoincMap.get(labEvents.getItem_id()));

        // ignore lab tests that does not have the primary unit
        // @TODO: a special case of "SECONDS"
        String observedUnit = labEvents.getValue_uom();
        String primaryUnit = primaryUnits.get(labEvents.getItem_id());
        if (!observedUnit.equals(primaryUnit)){
            return Optional.empty();
        }

        // placeholder of interpretation code
        String code = null;

        // handle lab tests with numeric outputs
        Double numericResult = labEvents.getValue_num();
        Double mean = primaryMeans.get(labEvents.getItem_id());
        if (numericResult != Double.MAX_VALUE) {
            String loincScale = loincEntryMap.get(loincId).getScale();

            if (labEvents.getFlag().equals("abnormal") && numericResult > mean) {
                if (loincScale.equals("Qn")){
                    code = "H";
                }
                if (loincScale.equals("Ord")){
                    code = "POS";
                } else {
                    throw new RuntimeException("None Qn nor Ord but has a numeric output");
                }
            }

            if (labEvents.getFlag().equals("abnormal") && numericResult < mean) {
                if (loincScale.equals("Qn")) {
                    code = "L";
                }
                if (loincScale.equals("Ord")) {
                    code = "NEG";
                } else {
                    throw new RuntimeException("None Qn nor Ord but has a numeric output");
                }
            }

            if (labEvents.getFlag().isEmpty()) {
                if (loincScale.equals("Qn")) {
                    code = "N";
                }
                if (loincScale.equals("Ord")) {
                    code = "NEG";
                } else {
                    throw new RuntimeException("None Qn nor Ord but has a numeric output");
                }
            }
        }

        // handle lab tests with String outputs
        else {
            // do something to convert String result to a coded value

        }

        HpoTerm4TestOutcome result = annotationMap.get(loincId).getCandidateHpoTerms().get(new Code(new Coding().setSystem("FHIR").setCode(code)));

        return Optional.of(result);
    }
}
