package org.jax.Entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "LabHpo")
public class JHULabHpo {

    @Id
    @Column(name = "ROW_ID")
    String rowid;
    @Column(name = "NEGATED")
    String negated;
    @Column(name = "MAP_TO")
    String mapTo;

    public JHULabHpo(String rowid, String negated, String mapTo) {
        this.rowid = rowid;
        this.negated = negated;
        this.mapTo = mapTo;
    }

    public String getRowid() {
        return rowid;
    }

    public void setRowid(String rowid) {
        this.rowid = rowid;
    }

    public String getNegated() {
        return negated;
    }

    public void setNegated(String negated) {
        this.negated = negated;
    }

    public String getMapTo() {
        return mapTo;
    }

    public void setMapTo(String mapTo) {
        this.mapTo = mapTo;
    }

    @Override
    public String toString(){
        return String.format("%s, %s, %s", this.rowid, this.negated, this.mapTo);
    }
}
