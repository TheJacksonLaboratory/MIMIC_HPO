package org.jax.Entity;

import javax.persistence.*;

@Entity
@Table(name = "Inferred_LabHpo")
public class InferredLabHpo {
    @Id
    @GeneratedValue
    @Column (name = "ROW_ID")
    private int id;
    @Column (name = "LABEVENT_ROW_ID")
    private int foreign_id;
    @Column (name = "INFERRED_TO")
    private String inferred_to;

    public InferredLabHpo(int foreign_id, String inferred_to) {
        this.foreign_id = foreign_id;
        this.inferred_to = inferred_to;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getForeign_id() {
        return foreign_id;
    }

    public void setForeign_id(int foreign_id) {
        this.foreign_id = foreign_id;
    }

    public String getInferred_to() {
        return inferred_to;
    }

    public void setInferred_to(String inferred_to) {
        this.inferred_to = inferred_to;
    }
}
