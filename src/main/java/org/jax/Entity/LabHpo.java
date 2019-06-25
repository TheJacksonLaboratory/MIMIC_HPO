package org.jax.Entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "LabHpo")
public class LabHpo {

    @Id
    @Column(name = "ROW_ID")
    int rowid;
    @Column(name = "NEGATED")
    char negated;
    @Column(name = "MAP_TO")
    String mapTo;

    public LabHpo(int rowid, char negated, String mapTo) {
        this.rowid = rowid;
        this.negated = negated;
        this.mapTo = mapTo;
    }

    public int getRowid() {
        return rowid;
    }

    public void setRowid(int rowid) {
        this.rowid = rowid;
    }

    public char getNegated() {
        return negated;
    }

    public void setNegated(char negated) {
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
        return String.format("%d, %s, %s", this.rowid, this.negated, this.mapTo);
    }
}
