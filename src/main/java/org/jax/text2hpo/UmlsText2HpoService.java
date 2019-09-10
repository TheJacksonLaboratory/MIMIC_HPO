package org.jax.text2hpo;

import org.jax.uni_phenominer.core.miner.metamap_local.MetaMapLocalHpoMiner;
import org.jax.uni_phenominer.core.miner.metamap_webAPI.MetaMapHPOMiner;
import org.jax.uni_phenominer.core.term.MinedTerm;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
public class UmlsText2HpoService {

    @Autowired
    MetaMapHPOMiner metaMapHPOMiner;

    @Autowired
    MetaMapLocalHpoMiner metaMapLocalHpoMiner;

    public Set<PositionUnawareTextMinedTerm> minedTerms(String query){
        Set<PositionUnawareTextMinedTerm> uniqueTerms = new HashSet<>();
        List<List<MinedTerm>> mineresults = metaMapLocalHpoMiner.doMining(query);
        for (List<MinedTerm> list : mineresults){
            for (MinedTerm minedTerm : list){
                PositionUnawareTextMinedTerm minedTermWithHpoId = new PositionUnawareTextMinedTerm(
                        minedTerm.isPresent(), minedTerm.getTermId());
                uniqueTerms.add(minedTermWithHpoId);
            }
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
