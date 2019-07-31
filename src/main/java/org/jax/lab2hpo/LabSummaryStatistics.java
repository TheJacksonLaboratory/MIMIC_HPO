package org.jax.lab2hpo;

public class LabSummaryStatistics {
	
	private Integer itemId;
	private String valueuom;
	private String loinc;
	private Integer counts;
	private Double mean_all;
	private Double min_normal;
	private Double mean_normal;
	private Double max_normal;
	
	// Default constructor
	public LabSummaryStatistics() {
		
	}

	public LabSummaryStatistics(Integer itemId, String valueuom, Integer counts, Double mean_all, Double min_normal,
			Double mean_normal, Double max_normal) {
		super();
		this.itemId = itemId;
		this.valueuom = valueuom;
		this.counts = counts;
		this.mean_all = mean_all;
		this.min_normal = min_normal;
		this.mean_normal = mean_normal;
		this.max_normal = max_normal;
	}

	public Integer getItemId() {
		return itemId;
	}

	public void setItemId(Integer itemId) {
		this.itemId = itemId;
	}

	public String getValueuom() {
		return valueuom;
	}

	public void setValueuom(String valueuom) {
		this.valueuom = valueuom;
	}

	public String getLoinc() {
		return loinc;
	}

	public void setLoinc(String loinc) {
		this.loinc = loinc;
	}

	public Integer getCounts() {
		return counts;
	}

	public void setCounts(Integer counts) {
		this.counts = counts;
	}

	public Double getMean_all() {
		return mean_all;
	}

	public void setMean_all(Double mean_all) {
		this.mean_all = mean_all;
	}

	public Double getMin_normal() {
		return min_normal;
	}

	public void setMin_normal(Double min_normal) {
		this.min_normal = min_normal;
	}

	public Double getMean_normal() {
		return mean_normal;
	}

	public void setMean_normal(Double mean_normal) {
		this.mean_normal = mean_normal;
	}

	public Double getMax_normal() {
		return max_normal;
	}

	public void setMax_normal(Double max_normal) {
		this.max_normal = max_normal;
	}

	@Override
	public String toString() {
		return "LabSummaryStatistics [itemId=" + itemId + ", valueuom=" + valueuom + ", loinc=" + loinc + ", counts="
				+ counts + ", mean_all=" + mean_all + ", min_normal=" + min_normal + ", mean_normal=" + mean_normal
				+ ", max_normal=" + max_normal + "]";
	}

}
