# Multicollinearity Analysis



For every correlated pair, we should ask three questions before acting:

1. Is this correlation **logical/biological** or a **data artifact**?
2. If I drop one, do I **lose information** or just **remove redundancy**?
3. Can I **engineer a better feature** that captures the relationship more cleanly than either raw column?

Logical correlations are reflections of reality. The correlation matrix is not a deletion list! it is a **feature engineering roadmap**.

---

## Cluster 1 -- The Age Cluster

| Pair | Correlation |
|------|-------------|
| `age_days` ↔ `hubbard_standard_weight_g` | 0.990 |
| `age_days` ↔ `target_temp_for_age_c` | -0.974 |
| `age_days` ↔ `feed_per_bird_g` | 0.969 |
| `hubbard_standard_weight_g` ↔ `target_temp_for_age_c` | -0.943 |
| `hubbard_standard_weight_g` ↔ `feed_per_bird_g` | 0.939 |
| `feed_per_bird_g` ↔ `target_temp_for_age_c` | -0.965 |

**Why they correlate:** `hubbard_standard_weight_g` and `target_temp_for_age_c` are lookup tables indexed by `age_days`. They are all expressions of the same biological clock, not independent features.

### Actions

| Column | Action | Reason |
|--------|--------|--------|
| `age_days` | **Keep** | Root cause of the cluster; keep the cause, drop the derivatives |
| `hubbard_standard_weight_g` | **Engineer → Drop** | Use only to compute `weight_deviation = avg_weight_g - hubbard_standard_weight_g`, then drop |
| `target_temp_for_age_c` | **Engineer → Drop** | Use only to compute `temp_deviation = temp_inside_avg_c - target_temp_for_age_c`, then drop |
| `feed_per_bird_g` | **Keep** | Captures actual consumption behavior, not just age-expected intake — real behavioral signal beyond `age_days` |

---

## Cluster 2 -- The Temperature Cluster

| Pair | Correlation |
|------|-------------|
| `temp_inside_max_c` ↔ `temp_inside_avg_c` | 0.986 |
| `temp_inside_min_c` ↔ `temp_inside_avg_c` | 0.986 |
| `temp_inside_min_c` ↔ `temp_inside_max_c` | 0.973 |

**Why they correlate:** Three measurements of the same physical quantity from three angles.

### Actions

| Column | Action | Reason |
|--------|--------|--------|
| `temp_inside_avg_c` | **Keep** | Most stable daily summary (level) |
| `temp_inside_min_c` | **Engineer → Drop** | Use with max to compute `temp_range_c`, then drop |
| `temp_inside_max_c` | **Engineer → Drop** | Same — `temp_range_c = temp_inside_max_c - temp_inside_min_c` |
| `temp_range_c` | **Engineer & Keep** | Captures daily thermal volatility — a house swinging 22°C→38°C stresses birds even if average looks fine |

**Result:** Two non-redundant temperature features: `temp_inside_avg_c` (level) + `temp_range_c` (volatility), plus `temp_deviation` from Cluster 1.

---

## Cluster 3 -- Feed & Water

| Pair | Correlation |
|------|-------------|
| `feed_consumed_kg` ↔ `water_consumed_L` | 0.990 |
| `feed_consumed_kg` ↔ `feed_per_bird_g` | 0.810 |
| `feed_per_bird_g` ↔ `water_consumed_L` | 0.804 |

**Why they correlate:** Birds drink ~1.8–2.0 L per kg of feed under normal conditions. The ratio is biologically stable — deviations are a disease signal (water drops before feed when birds are sick).

### Actions

| Column | Action | Reason |
|--------|--------|--------|
| `water_to_feed_ratio` | **Engineer & Keep** | `water_consumed_L / feed_consumed_kg` — early warning signal, ratio drop = disease indicator |
| `feed_per_bird_g` | **Keep** | Primary feed feature, already normalized for flock size |
| `feed_consumed_kg` | **Keep for now** | Monitor feature importance post-modeling; drop if redundant |
| `water_consumed_L` | **Keep** | Independent early warning signal; lag features planned |

> **Note:** If switching from tree-based to linear models, drop `feed_consumed_kg` and keep only `feed_per_bird_g` + ratio.

---

## Cluster 4 -- Flock Size

| Pair | Correlation |
|------|-------------|
| `placement_count` ↔ `current_flock_size` | 0.929 |
| `placement_count` ↔ `house_area_m2` | 0.878 |

### Actions

| Column | Action | Reason |
|--------|--------|--------|
| `placement_count` | **Keep** | Static Day-1 property, only non-leaking flock scale feature |
| `current_flock_size` | **Drop (LEAKAGE)** | Verified: `current_flock_size = placement_count - cumulative_deaths - cumulative_culls` with zero deviation across all 74,354 rows. Includes today's deaths. Keeping it while dropping cumulative targets lets the model reconstruct mortality trivially. |
| `survival_rate_to_date` | **Do NOT engineer** | Would be `current_flock_size / placement_count` = complement of `cumulative_mortality_pct`. Leakage by construction. |
| `house_area_m2` | **Keep** | 0.878 correlation with `placement_count` is just farm management reality (bigger houses → more birds). Already captured by `stocking_density_per_m2`. No action needed. |

---

## Cluster 5 -- Leakage Columns (Target Derivatives)

| Pair | Correlation |
|------|-------------|
| `daily_deaths` ↔ `daily_mortality_pct` | 0.957 |
| `cumulative_deaths` ↔ `cumulative_mortality_pct` | 0.925 |
| `cumulative_culls` ↔ `cumulative_mortality_pct` | 0.896 |
| `daily_deaths` ↔ `daily_culls` | 0.849 |

### Actions

| Column | Action |
|--------|--------|
| `daily_deaths` | **Drop — leakage** |
| `daily_culls` | **Drop — leakage** |
| `cumulative_deaths` | **Drop — leakage** |
| `cumulative_culls` | **Drop — leakage** |
| `cumulative_mortality_pct` | **Drop — leakage** |
| `daily_mortality_pct` | **Keep — regression target** |
| `mortality_spike` | **Drop — leakage** (derived from target: 1 if `daily_mortality_pct > 0.30%`) |

---

## Other Drops (Non-Correlation)

| Column | Action | Reason |
|--------|--------|--------|
| `house_total_cycles` | **Drop** | Verified identical to `cycle_number` (correlation = 1.0, 100% rows equal) |

---

## Full Decision Table

| Column | Action | Category |
|--------|--------|----------|
| `age_days` | Keep | Age cluster root |
| `hubbard_standard_weight_g` | Engineer `weight_deviation` → Drop | Age derivative |
| `target_temp_for_age_c` | Engineer `temp_deviation` → Drop | Age derivative |
| `feed_per_bird_g` | Keep | Behavioral signal |
| `temp_inside_avg_c` | Keep | Temperature level |
| `temp_inside_min_c` | Engineer `temp_range_c` → Drop | Temperature redundancy |
| `temp_inside_max_c` | Engineer `temp_range_c` → Drop | Temperature redundancy |
| `temp_range_c` | Engineer & Keep | Thermal volatility (new) |
| `water_to_feed_ratio` | Engineer & Keep | Disease early warning (new) |
| `feed_consumed_kg` | Keep for now | Monitor post-modeling |
| `water_consumed_L` | Keep | Early warning, lags planned |
| `placement_count` | Keep | Only non-leaking scale feature |
| `current_flock_size` | **Drop** | Leakage |
| `house_total_cycles` | **Drop** | Redundant with `cycle_number` |
| `daily_deaths` | **Drop** | Leakage |
| `daily_culls` | **Drop** | Leakage |
| `cumulative_deaths` | **Drop** | Leakage |
| `cumulative_culls` | **Drop** | Leakage |
| `cumulative_mortality_pct` | **Drop** | Leakage |
| `daily_mortality_pct` | **Keep** | **Regression target** |
| `mortality_spike` | **Drop** | Derived from target — leakage |

---

## Engineered Features Summary

| New Feature | Formula | Signal |
|-------------|---------|--------|
| `weight_deviation` | `avg_weight_g - hubbard_standard_weight_g` | Underweight = sick/underfed flock |
| `temp_deviation` | `temp_inside_avg_c - target_temp_for_age_c` | Heat/cold stress relative to age |
| `temp_range_c` | `temp_inside_max_c - temp_inside_min_c` | Daily thermal volatility |
| `water_to_feed_ratio` | `water_consumed_L / feed_consumed_kg` | Ratio drop = early disease signal |

---

## Key Principle

Any column that is a mathematical function of cumulative deaths/culls is leakage, regardless of its name. `current_flock_size` is `placement_count` minus cumulative mortality — the same leakage wearing a different label.
