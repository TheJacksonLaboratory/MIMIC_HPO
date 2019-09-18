package org.jax.text2hpo;

import org.apache.commons.lang3.StringUtils;
import org.jax.uni_phenominer.core.miner.TermMinerException;
import org.jax.uni_phenominer.core.miner.metamap_local.MetaMapLocalHpoMiner;
import org.jax.uni_phenominer.core.term.MinedTerm;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class UmlsText2HpoService {

    @Autowired
    //switch to other miner if desired, such as MetaMapHPOMiner (using web API)
    private MetaMapLocalHpoMiner miner;

    public Collection<PositionUnawareTextMinedTerm> minedTerms_single(String query){
        try {
            Collection<MinedTerm> mineresults = miner.mine(query);
            return uniqueTerms(mineresults);
        } catch (TermMinerException e) {
            e.printStackTrace();
        }

        return new HashSet<>();
    }

    public List<Set<PositionUnawareTextMinedTerm>> minedTerms_batch(Collection<String> queries){
        // this is specific to MetaMapLocalHpoMiner
        MetaMapLocalHpoMiner metaMapLocalHpoMiner = (MetaMapLocalHpoMiner) miner;

        metaMapLocalHpoMiner.getMetaMapApi().resetOptions();
        metaMapLocalHpoMiner.getMetaMapApi().setOptions("-R HPO -i");

        String queries_joined = StringUtils.join(queries, "\n\n");
        List<List<MinedTerm>> mineresults = metaMapLocalHpoMiner.doMining(queries_joined);

        List<Set<PositionUnawareTextMinedTerm>> mineresults_strip_position = new ArrayList<>();
        for (List<MinedTerm> mineresult : mineresults){
            mineresults_strip_position.add(uniqueTerms(mineresult));
        }
        return mineresults_strip_position;
    }

    private Set<PositionUnawareTextMinedTerm> uniqueTerms(Collection<MinedTerm> minedTerms){
        Set<PositionUnawareTextMinedTerm> uniqueTerms = new HashSet<>();
        for (MinedTerm minedTerm : minedTerms){
            PositionUnawareTextMinedTerm minedTermWithHpoId = new PositionUnawareTextMinedTerm(
                    minedTerm.isPresent(), minedTerm.getTermId());
            uniqueTerms.add(minedTermWithHpoId);
        }
        return uniqueTerms;
    }


    public static class PositionUnawareTextMinedTerm {
        private boolean isPresent;
        private String termid;

        public PositionUnawareTextMinedTerm(boolean isPresent, String termid) {
            this.isPresent = isPresent;
            this.termid = termid;
        }

        public boolean isPresent() {
            return isPresent;
        }

        public void setPresent(boolean present) {
            isPresent = present;
        }

        public String getTermid() {
            return termid;
        }

        public void setTermid(String termid) {
            this.termid = termid;
        }

        @Override
        public boolean equals(Object other){
            PositionUnawareTextMinedTerm o = (PositionUnawareTextMinedTerm) other;
            return this.isPresent == o.isPresent && this.termid.equals(o.termid);
        }

        @Override
        public int hashCode(){
            return ((Boolean) this.isPresent).hashCode() + 31 * this.termid.hashCode();
        }

    }

}
