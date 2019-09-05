package org.jax.Entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

@Entity
public class NoteHpo {
    @Id
    @GeneratedValue
    @Column(name = "ROW_ID")
    int rowid;
    @Column(name = "NOTES_ROW_ID")
    int rowid_note;
    @Column(name = "NEGATED")
    String negated;
    @Column(name = "MAP_TO")
    String mapTo;

    public NoteHpo(int rowid_note, String negated, String mapTo) {
        this.rowid_note = rowid_note;
        this.negated = negated;
        this.mapTo = mapTo;
    }

    public int getRowid() {
        return rowid;
    }

    public void setRowid(int rowid) {
        this.rowid = rowid;
    }

    public int getRowid_note() {
        return rowid_note;
    }

    public void setRowid_note(int rowid_note) {
        this.rowid_note = rowid_note;
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
        return String.format("%d, %d, %s, %s", this.rowid, this.rowid_note, this.negated, this.mapTo);
    }
}
