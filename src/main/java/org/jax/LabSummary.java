package org.jax;

import javax.annotation.Nullable;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Summaries of quantitative lab events
 */
public class LabSummary {

    private int id; //local lab test id
    private Map<String, Double> meanByUnit;
    private Map<String, Integer> countByUnit;
    private Map<String, NormalRange> normalRangeByUnit;


    public LabSummary(int id){
        this.id = id;
        this.meanByUnit = new HashMap<>();
        this.countByUnit = new HashMap<>();
        this.normalRangeByUnit = new HashMap<>();
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
     * @param unit unit of the lab test
     * @param count the count of lab tests with the specified unit
     * @param mean the mean value of all lab tests, normal and abnormal
     * @param min_normal a null value means that a min value for normal finding could not be established
     * @param max_normal a null value means that a max value for normal finding could not be established
     */
    public void put(String unit, int count, double mean, @Nullable Double min_normal, @Nullable
            Double max_normal) {
        this.countByUnit.put(unit, count);
        this.meanByUnit.put(unit, mean);
        if (min_normal != null && max_normal != null) {
            this.normalRangeByUnit.put(unit, new NormalRange(min_normal, max_normal));
        }
    }

    public int getId() {
        return id;
    }

    public Map<String, Double> getMeanByUnit() {
        return meanByUnit;
    }

    public Map<String, Integer> getCountByUnit() {
        return this.countByUnit;
    }

    public Map<String, NormalRange> getNormalRangeByUnit() {
        return this.normalRangeByUnit;
    }

    public Optional<String> getPrimaryUnit() {
        return this.countByUnit.entrySet().stream()
                .sorted(Map.Entry.comparingByValue((a, b) -> b - a))
                .map(e -> e.getKey()).findFirst();
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

    public static class NormalRange {
        private double min;
        private double max;

        NormalRange(double min, double max) {
            this.min = min;
            this.max = max;
        }

        public double getMin() {
            return min;
        }

        public void setMin(double min) {
            this.min = min;
        }

        public double getMax() {
            return max;
        }

        public void setMax(double max) {
            this.max = max;
        }
    }

}
