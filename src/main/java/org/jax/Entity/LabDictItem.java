package org.jax.Entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "D_LABITEMS")
public class LabDictItem {

    @Id
    @Column(name = "ROW_ID")
    private int rowId;
    @Column(name = "ITEM_ID")
    private int itemId;
    @Column(name = "LABEL")
    private String label;
    @Column(name = "FLUID")
    private String fluid;
    @Column(name = "CATEGORY")
    private String category;
    @Column(name = "LOINC_Code")
    private String loincCode;

    public LabDictItem(int rowId, int itemId, String label, String fluid, String category, String loincCode) {
        this.rowId = rowId;
        this.itemId = itemId;
        this.label = label;
        this.fluid = fluid;
        this.category = category;
        this.loincCode = loincCode;
    }

    public int getRowId() {
        return rowId;
    }

    public void setRowId(int rowId) {
        this.rowId = rowId;
    }

    public int getItemId() {
        return itemId;
    }

    public void setItemId(int itemId) {
        this.itemId = itemId;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public String getFluid() {
        return fluid;
    }

    public void setFluid(String fluid) {
        this.fluid = fluid;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getLoincCode() {
        return loincCode;
    }

    public void setLoincCode(String loincCode) {
        this.loincCode = loincCode;
    }
}
