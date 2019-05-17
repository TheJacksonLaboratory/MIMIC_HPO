package org.jax;

import java.util.HashMap;
import java.util.Map;

/**
 * Summaries of quantitative lab events
 */
public class LabSummary {

    private int id; //local lab test id
    private Map<String, Double> meanByUnit;
    private Map<String, Integer> countByUnit;

    public LabSummary(int id){
        this.id = id;
        this.meanByUnit = new HashMap<>();
        this.countByUnit = new HashMap<>();
    }

    /**
     * Modify current lab summary by adding one lab result
     * @param unit
     * @param value
     */
    public void add(String unit, Double value){
        this.countByUnit.putIfAbsent(unit, 0);
        this.meanByUnit.putIfAbsent(unit, 0.0);
        int n = this.countByUnit.get(unit);
        double mean = this.meanByUnit.get(unit);
        double updated_mean = (mean * n + value) / (n + 1);
        this.meanByUnit.put(unit, updated_mean);
        this.countByUnit.put(unit, n + 1);
    }

    /**
     * Modify current lab summary by adding precomputed count and mean
     * @param unit
     * @param count
     * @param mean
     */
    public void put(String unit, int count, double mean) {
        this.countByUnit.put(unit, count);
        this.meanByUnit.put(unit, mean);
    }

    public int getId() {
        return id;
    }

    public Map<String, Double> getMeanByUnit() {
        return new HashMap<>(meanByUnit);
    }

    public Map<String, Integer> getCountByUnit() {
        return new HashMap<>(this.countByUnit);
    }

    @Override
    public String toString() {
        StringBuilder builder = new StringBuilder();
        builder.append("local_lab_id: " + id);
        builder.append("; ");
        for (String unit : this.countByUnit.keySet()) {
            builder.append(unit);
            builder.append("--");
            builder.append("count: " + this.countByUnit.get(unit));
            builder.append(" ; mean: ");
            builder.append(this.meanByUnit.get(unit));
            builder.append(" ");
        }
        return builder.toString();
    }


}
