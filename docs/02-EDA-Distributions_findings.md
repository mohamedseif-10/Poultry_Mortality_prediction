# Numeric Feature Distributions: Findings & Decisions

## 1. Key Distribution Patterns
![alt text](image.png)

### A. Bimodal Distributions (Overlapping Populations)
* **Features:** `doc_arrival_temp_c`, `feed_per_bird_g`, `temp_outside_avg_c`
* **Finding:** Two distinct peaks indicate hidden sub-populations. For `temp_outside_avg_c` and `doc_arrival_temp_c`, this is clearly seasonality (summer vs. winter). For `feed_per_bird_g`, it reflects different growth phases.
* **Decision:** Do not force these into a normal distribution. Tree-based models will naturally find the "valley" between peaks to split the populations. 

### B. Highly Skewed / Long-Tail Features
* **Features:** `wind_speed_kmh`, `water_consumed_L`, `ammonia_ppm`, `prev_cycle_mortality_pct`, `prev_cycle_fcr`, `placement_count`
* **Finding:** Most days are normal, but extreme events occur (e.g., Khamaseen dust storms driving wind speed, or severe ammonia spikes). 
* **Decision:** **Do not clip or winsorize.** In mortality prediction, the extreme right tail *is* the signal. A massive ammonia spike isn't an outlier to be smoothed; it's the cause of death.

### C. Discrete Features
* **Features:** `worker_count`, `hubbard_standard_weight_g`, `days_since_last_vaccine`
* **Finding:** `worker_count` is a discrete integer (1-8). `hubbard_standard_weight_g` is a lookup table value that steps up daily.
* **Decision:** Treat `worker_count` as ordinal, not continuous. The difference between 1 and 2 workers (holiday skeleton crew) is operationally different than 7 vs 8 workers.

## 2. Modeling Strategy

### Primary Choice: Tree-Based Models (XGBoost / LightGBM)
Given the distributions above, tree-based models are the mandatory baseline for this tabular data:
1. **Immunity to Skewness:** Trees split on rank order. They don't care about the massive right tail in `wind_speed_kmh`, saving us from complex log-transformations.
2. **Natural Bimodal Handling:** They easily isolate the summer/winter peaks in temperature data without needing manual flags.
3. **Explainability:** Farm managers need to know *why* an alert fired. Trees allow for SHAP value extraction ("Alert: Ammonia > 20ppm + Age > 30 days").

### Why Not Linear Models or Neural Networks?
Linear models and NNs require smooth, normally distributed data. To use them here, we would have to log-transform the skewed tails, scale everything, and manually encode the bimodal splits. This destroys the physical interpretability of the features (e.g., explaining "log-ammonia" to a farmer).
