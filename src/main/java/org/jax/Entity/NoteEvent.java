package org.jax.Entity;


import java.sql.Timestamp;

public class NoteEvent {

    private int row_id;
    private int subject_id;
    private int hadm_id;
    private Timestamp chartDate;
    private Timestamp chartTime;
    private Timestamp storetime;
    private String category;
    private String description;
    private int cgid;
    private String isError;
    private String text;

    public NoteEvent(int row_id, int subject_id, int hadm_id, Timestamp chartDate, Timestamp chartTime, Timestamp storetime, String category, String description, int cgid, String isError, String text) {
        this.row_id = row_id;
        this.subject_id = subject_id;
        this.hadm_id = hadm_id;
        this.chartDate = chartDate;
        this.chartTime = chartTime;
        this.storetime = storetime;
        this.category = category;
        this.description = description;
        this.cgid = cgid;
        this.isError = isError;
        this.text = text;
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

    public Timestamp getChartDate() {
        return chartDate;
    }

    public void setChartDate(Timestamp chartDate) {
        this.chartDate = chartDate;
    }

    public Timestamp getChartTime() {
        return chartTime;
    }

    public void setChartTime(Timestamp chartTime) {
        this.chartTime = chartTime;
    }

    public Timestamp getStoretime() {
        return storetime;
    }

    public void setStoretime(Timestamp storetime) {
        this.storetime = storetime;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public int getCgid() {
        return cgid;
    }

    public void setCgid(int cgid) {
        this.cgid = cgid;
    }

    public String getIsError() {
        return isError;
    }

    public void setIsError(String isError) {
        this.isError = isError;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }
}
