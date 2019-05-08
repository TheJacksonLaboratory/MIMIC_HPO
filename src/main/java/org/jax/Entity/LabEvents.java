package org.jax.Entity;

import java.sql.Timestamp;
import javax.persistence.*;

/**
 * Lab event class
 */
@Entity
@Table(name = "LABEVENTS")
public class LabEvents {

    @Id
    @Column(name = "ROW_ID")
    private int row_id;
    @Column(name = "SUBJECT_ID")
    private int subject_id;
    @Column(name = "HADM_ID")
    private int hadm_id;
    @Column(name = "ITEMID")
    private int item_id;
    @Column(name = "CHARTTIME")
    private Timestamp chart_time;
    @Column(name = "VALUE")
    private String value;
    @Column(name = "VALUENUM")
    private double value_num;
    @Column(name = "VALUEUOM")
    private String value_uom;
    @Column(name = "FLAG")
    private String flag;

    public LabEvents(int row_id, int subject_id, int hadm_id, int item_id, Timestamp chart_time, String value, double value_num, String value_uom, String flag) {
        this.row_id = row_id;
        this.subject_id = subject_id;
        this.hadm_id = hadm_id;
        this.item_id = item_id;
        this.chart_time = chart_time;
        this.value = value;
        this.value_num = value_num;
        this.value_uom = value_uom;
        this.flag = flag;
    }

    public int getRow_id() {
        return row_id;
    }

    public void setRow_id(int row_id) {
        this.row_id = row_id;
    }

    public int getSubject_id() {
        return subject_id;
    }

    public void setSubject_id(int subject_id) {
        this.subject_id = subject_id;
    }

    public int getHadm_id() {
        return hadm_id;
    }

    public void setHadm_id(int hadm_id) {
        this.hadm_id = hadm_id;
    }

    public int getItem_id() {
        return item_id;
    }

    public void setItem_id(int item_id) {
        this.item_id = item_id;
    }

    public Timestamp getChart_time() {
        return chart_time;
    }

    public void setChart_time(Timestamp chart_time) {
        this.chart_time = chart_time;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public double getValue_num() {
        return value_num;
    }

    public void setValue_num(double value_num) {
        this.value_num = value_num;
    }

    public String getValue_uom() {
        return value_uom;
    }

    public void setValue_uom(String value_uom) {
        this.value_uom = value_uom;
    }

    public String getFlag() {
        return flag;
    }

    public void setFlag(String flag) {
        this.flag = flag;
    }
}
