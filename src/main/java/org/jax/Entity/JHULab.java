package org.jax.Entity;

import javax.persistence.*;
import java.io.Serializable;
import java.sql.Date;

@Entity
@Table(name = "vw_pc_labs")
@IdClass(JHULab.JHULabId.class)
public class JHULab {

    /**
     * Class to represent the following table
     [PATID] [varchar](50) NOT NULL,
     [ENCOUNTERID] [varchar](50) NULL,
     [LAB_LOINC] [varchar](10) NULL,
     [RESULT_DATE] [date] NULL,
     [RESULT_TIME] [varchar](8) NULL,
     [RESULT_NUM] [float] NULL,
     [LOINC_LONG_COMMON_NAME] [nvarchar](255) NULL,
     [LOINC_SHORTNAME] [nvarchar](255) NULL,
     [LOINC_UNIT] [nvarchar](50) NULL,
     [RANGE_LOW] [varchar](10) NULL,
     [RANGE_HIGH] [varchar](10) NULL,
     */


    @Column(name = "PATID")
    @Id
    private String patiend_id;
    @Column(name = "ENCOUNTERID")
    @Id
    private String encounter_id;
    @Column(name = "LAB_LOINC")
    private String loinc_id;
    @Column(name = "RESULT_DATE")
    private Date result_date;
    @Column(name = "RESULT_TIME")
    private String result_time;
    @Column(name = "RESULT_NUM")
    private Float result_num;
    @Column(name = "LOINC_LONG_COMMON_NAME")
    private String loinc_long_common_name;
    @Column(name = "LOINC_SHORTNAME")
    private String loinc_short_name;
    @Column(name = "LOINC_UNIT")
    private String loinc_unit;
    @Column(name = "RANGE_LOW")
    private String range_low;
    @Column(name = "RANGE_HIGH")
    private String range_high;

    public JHULab(String patiend_id, String encounter_id, String loinc_id, Date result_date, String result_time, Float result_num, String loinc_long_common_name, String loinc_short_name, String loinc_unit, String range_low, String range_high) {
        this.patiend_id = patiend_id;
        this.encounter_id = encounter_id;
        this.loinc_id = loinc_id;
        this.result_date = result_date;
        this.result_time = result_time;
        this.result_num = result_num;
        this.loinc_long_common_name = loinc_long_common_name;
        this.loinc_short_name = loinc_short_name;
        this.loinc_unit = loinc_unit;
        this.range_low = range_low;
        this.range_high = range_high;
    }

    public String getPatiend_id() {
        return patiend_id;
    }

    public void setPatiend_id(String patiend_id) {
        this.patiend_id = patiend_id;
    }

    public String getEncounter_id() {
        return encounter_id;
    }

    public void setEncounter_id(String encounter_id) {
        this.encounter_id = encounter_id;
    }

    public String getLoinc_id() {
        return loinc_id;
    }

    public void setLoinc_id(String loinc_id) {
        this.loinc_id = loinc_id;
    }

    public Date getResult_date() {
        return result_date;
    }

    public void setResult_date(Date result_date) {
        this.result_date = result_date;
    }

    public String getResult_time() {
        return result_time;
    }

    public void setResult_time(String result_time) {
        this.result_time = result_time;
    }

    public Float getResult_num() {
        return result_num;
    }

    public void setResult_num(Float result_num) {
        this.result_num = result_num;
    }

    public String getLoinc_long_common_name() {
        return loinc_long_common_name;
    }

    public void setLoinc_long_common_name(String loinc_long_common_name) {
        this.loinc_long_common_name = loinc_long_common_name;
    }

    public String getLoinc_short_name() {
        return loinc_short_name;
    }

    public void setLoinc_short_name(String loinc_short_name) {
        this.loinc_short_name = loinc_short_name;
    }

    public String getLoinc_unit() {
        return loinc_unit;
    }

    public void setLoinc_unit(String loinc_unit) {
        this.loinc_unit = loinc_unit;
    }

    public String getRange_low() {
        return range_low;
    }

    public void setRange_low(String range_low) {
        this.range_low = range_low;
    }

    public String getRange_high() {
        return range_high;
    }

    public void setRange_high(String range_high) {
        this.range_high = range_high;
    }


    public static class JHULabId implements Serializable{
        private String patiend_id;
        private String encounter_id;
    }
}
