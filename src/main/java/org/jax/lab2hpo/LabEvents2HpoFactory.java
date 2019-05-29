package org.jax.lab2hpo;

import org.hl7.fhir.dstu3.model.Coding;
import org.jax.Entity.LabEvent;
import org.jax.service.LocalLabTestNotMappedToLoinc;
import org.monarchinitiative.loinc2hpo.codesystems.Code;
import org.monarchinitiative.loinc2hpo.exception.LoincCodeNotAnnotatedException;
import org.monarchinitiative.loinc2hpo.exception.MalformedLoincCodeException;
import org.monarchinitiative.loinc2hpo.exception.UnrecognizedCodeException;
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
    // mean value for quantitative lab tests, key is the item_id
    // obtained from LabSummaryParser
    private Map<Integer, Double> primaryMeans;
    // normal range for quantitative lab tests, key is the primary unit
    private Map<Integer, LabSummary> labSummaryMap;


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

    public LabEvents2HpoFactory(Map<Integer, String> local2LoincMap,
                                Map<Integer, LabSummary> labSummaryMap,
                                Map<LoincId, LOINC2HpoAnnotationImpl> annotationMap,
                                Map<LoincId, LoincEntry> loincEntryMap) {
        this.local2LoincMap = local2LoincMap;
        this.labSummaryMap = labSummaryMap;
        this.annotationMap = annotationMap;
        this.loincEntryMap = loincEntryMap;
    }

    public Optional<HpoTerm4TestOutcome> convert2(LabEvent labEvent) throws LocalLabTestNotMappedToLoinc, MalformedLoincCodeException, LoincCodeNotAnnotatedException, UnrecognizedUnitException, UnableToInterpretateException, UnrecognizedCodeException {
        LoincId loincId = null;

        // check if local lab test code is mapped to loinc
        int item_id = labEvent.getItem_id();
        if (! local2LoincMap.containsKey(item_id)) {
            logger.warn("cannot map local item_id to loinc: " + item_id);
            throw new LocalLabTestNotMappedToLoinc();
        }

        //throws MalformedLoincCodeException
        loincId = new LoincId(local2LoincMap.get(item_id));


        //check whether the loinc is annotated
        if (!annotationMap.containsKey(loincId)) {
            throw new LoincCodeNotAnnotatedException();
        }
        logger.info("annotation map contains " + loincId.toString());
        logger.info("annotation map for " + loincId.toString() + "candidate mappings: " + annotationMap.get(loincId).getCandidateHpoTerms().size());

        String loincScale = loincEntryMap.get(loincId).getScale();
        LabSummary labSummary = labSummaryMap.get(item_id);


        // placeholder of interpretation code
        String code = null;

        if (loincScale.equals("Qn")) {
            code = numericLab2hpo(labEvent, labSummary, "Qn").orElse(null);
        } else if (loincScale.equals("Ord")) {
            code = numericLab2hpo(labEvent, labSummary, "Ord").orElse(null);
        } else {
            code = null;
        }


            // if lab result has numeric result
        // check the unit, compare with the reference range
        // if such reference does not exist, fail the mapping
        // if a reference can be found
        // for Qn test, map to "L", "H", or "N"
        // for Ord test, map to "NEG", "POS"
        // ignore Nom tests for now
        // if lab result does not have numeric result
        // check the value field, use regular expression to determine it

        if (code == null) {
            throw new UnableToInterpretateException();
        } else {
            Code interpretation = new Code(new Coding().setSystem("FHIR").setCode(code));
            logger.info("interpretation code: " + interpretation.toString());
            //annotationMap.get(loincId).getCandidateHpoTerms().keySet().forEach(k -> System.out.println(k.toString()));

            LOINC2HpoAnnotationImpl annotation = annotationMap.get(loincId);
            if (annotation.getCandidateHpoTerms().containsKey(interpretation)) {
                return Optional.of(annotation.getCandidateHpoTerms().get(interpretation));
            } else {
                throw new UnrecognizedCodeException("Interpretation code is not mapped to hpo");
            }
        }

    }

    private Optional<String> numericLab2hpo(LabEvent labEvent, LabSummary labSummary, String scale) {
        if (labSummary == null) {
            System.out.println(labEvent.getItem_id());
        }
        String primaryUnit = labSummary.getPrimaryUnit();
        String observedUnit = labEvent.getValue_uom();
        if (observedUnit.equals(primaryUnit)) {
            return numericWithPrimaryUnit(labEvent, labSummary, scale);
        } else {
            return numericNonPrimaryUnit(labEvent, labSummary, scale);
        }

    }

    private Optional<String> numericWithPrimaryUnit(LabEvent labEvent, LabSummary labSummary, String scale) {
        String unit = labEvent.getValue_uom();
        LabSummary.NormalRange normalRange = labSummary.getNormalRangeByUnit().get(unit);
        double min_normal = normalRange.getMin();
        double max_normal = normalRange.getMax();
        double observed_value = labEvent.getValue_num();
        String flag = labEvent.getFlag();
        String code = null;

        if (scale.equals("Qn")) {
            if (observed_value < min_normal) {
                code = "L";
            } else if (observed_value > max_normal) {
                code = "H";
            } else {
                code = "N";
            }
        } else if (scale.equals("Ord")) {
            if (observed_value < min_normal) {
                code = "NEG";
            } else {
                code = "POS";
            }
        } else {
            // do not deal with other types
            code = null;
        }
        return Optional.of(code);
    }

    private Optional<String> numericNonPrimaryUnit(LabEvent labEvent, LabSummary labSummary, String scale) {

        //TODO: implement some special cases later
        return Optional.empty();


    }

    private Optional<HpoTerm4TestOutcome> nonNumericLab2Hpo(LabEvent labEvent, LabSummary labSummary) {
        //TODO: implement
        return Optional.empty();

    }

    public Optional<HpoTerm4TestOutcome> convert(LabEvent labEvent) throws
            LocalLabTestNotMappedToLoinc,
            MalformedLoincCodeException,
            LoincCodeNotAnnotatedException,
            UnrecognizedCodeException {

        LoincId loincId = null;

        // check if local lab test code is mapped to loinc
        int item_id = labEvent.getItem_id();
        if (! local2LoincMap.containsKey(item_id)) {
            logger.warn("cannot map local item_id to loinc: " + item_id);
            throw new LocalLabTestNotMappedToLoinc();
        }

        //throws MalformedLoincCodeException
        loincId = new LoincId(local2LoincMap.get(item_id));


        //check whether the loinc is annotated
        if (!annotationMap.containsKey(loincId)) {
            throw new LoincCodeNotAnnotatedException();
        }
        logger.info("annotation map contains " + loincId.toString());
        logger.info("annotation map for " + loincId.toString() + "candidate mappings: " + annotationMap.get(loincId).getCandidateHpoTerms().size());


        // placeholder of interpretation code
        String code = null;


        // if lab result has numeric result
            // check the unit, compare with the reference range
                // if such reference does not exist, fail the mapping
                // if a reference can be found
                    // for Qn test, map to "L", "H", or "N"
                    // for Ord test, map to "NEG", "POS"
                    // ignore Nom tests for now
        // if lab result does not have numeric result
            // check the value field, use regular expression to determine it

        // handle lab tests with numeric outputs
        double numericResult = labEvent.getValue_num();
        // could be null, represented as Double.MAX_VALUE
        // in addition, we need the primary mean value
        if (numericResult != Double.MAX_VALUE && primaryMeans.containsKey(item_id)) {

            // ignore lab tests that does not have the primary unit
            // @TODO: a special case of "SECONDS"
            String observedUnit = labEvent.getValue_uom().replace("\"", "");
            String primaryUnit = primaryUnits.get(labEvent.getItem_id());
            if (!observedUnit.equals(primaryUnit)){
                logger.info(String.format("observed unit: %s, expected unit: %s", observedUnit, primaryUnit));
                return Optional.empty();
            }


            double mean = primaryMeans.get(item_id);
            String loincScale = loincEntryMap.get(loincId).getScale();
            logger.info("loincScale: " + loincScale);
            logger.info(String.format("result: %f, mean: %f", numericResult, mean));
            if (labEvent.getFlag().equals("abnormal") && numericResult > mean) {

                if (loincScale.equals("Qn")){
                    code = "H";
                } else if (loincScale.equals("Ord")){
                    code = "POS";
                } else {
                    return Optional.empty();
                    //throw new RuntimeException("None Qn nor Ord but has a numeric output");
                }
            }

            if (labEvent.getFlag().equals("abnormal") && numericResult < mean) {
                if (loincScale.equals("Qn")) {
                    code = "L";
                } else if (loincScale.equals("Ord")) {
                    code = "NEG";
                } else {
                    return Optional.empty();
                    //throw new RuntimeException("None Qn nor Ord but has a numeric output");
                }
            }

            if (labEvent.getFlag().isEmpty()) {
                if (loincScale.equals("Qn")) {
                    code = "N";
                } else if (loincScale.equals("Ord")) {
                    code = "NEG";
                } else {
                    return Optional.empty();
                    //throw new RuntimeException("None Qn nor Ord but has a numeric output");
                }
            }
        }

        // handle lab tests with String outputs
        else {
            // do something to convert String result to a coded value
            if (labEvent.getValue().toUpperCase().equals("NORMAL")) {
                System.out.println("NORMAL detected");
            }
            if (labEvent.getValue().toLowerCase().matches("normal")){
                code = "N";
            }
            return Optional.empty();

        }

        if (code == null) {
            return Optional.empty();
        } else {
            Code interpretation = new Code(new Coding().setSystem("FHIR").setCode(code));
            logger.info("interpretation code: " + interpretation.toString());
            //annotationMap.get(loincId).getCandidateHpoTerms().keySet().forEach(k -> System.out.println(k.toString()));

            LOINC2HpoAnnotationImpl annotation = annotationMap.get(loincId);
            if (annotation.getCandidateHpoTerms().containsKey(interpretation)) {
                return Optional.of(annotation.getCandidateHpoTerms().get(interpretation));
            } else {
                return Optional.empty();
            }
        }



//        // check whether the code has an hpo mapping
//        if (! annotationMap.get(loincId).getCandidateHpoTerms().containsKey(interpretation)) {
//            throw new UnrecognizedCodeException();
//        }


    }
}
