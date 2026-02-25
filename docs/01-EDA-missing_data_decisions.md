# Handling missing data:  Findings, Decisions & Tradeoffs



## Decisions by Category

### 1. Sparse Rows (Event-Based Not Truly Missing)
These columns are NaN on days when no event occurred. That's expected behavior, not data loss.

| Column | Action | Derive What |
|--------|--------|-------------|
| `antibiotic_name` | Derive → Drop original | See antibiotic plan below |
| `vaccine_given` | Derive → Drop original | `cumulative_vaccine_count`, `vaccine_compliance_flag`, `days_in_vaccine_window` |
| `vaccine_route` | Derive → Drop original | Flock-level primary route (mode) |
| `scheduled_vaccine_today` | Derive → Drop original | `vaccine_compliance` (scheduled vs actually given) |

> **Open question (vaccines only)**: Different vaccines have different active windows. Need domain lookup or conservative default.

#### Antibiotic Feature Plan (Finalized)

Only 5 unique drugs (Colistin, Amoxicillin, Doxycycline, Tylosin, Enrofloxacin) — low cardinality, one-hot encode directly.

| Feature | Type | Source |
|---------|------|--------|
| `antibiotic_Colistin` | binary | One-hot from `antibiotic_name` |
| `antibiotic_Amoxicillin` | binary | One-hot |
| `antibiotic_Doxycycline` | binary | One-hot |
| `antibiotic_Tylosin` | binary | One-hot |
| `antibiotic_Enrofloxacin` | binary | One-hot |
| `antibiotic_severity` | ordinal 0–5 | Domain-based: Enrofloxacin=5, Colistin=4, Amoxicillin=3, Doxycycline=2, Tylosin=1, None=0 |
| `days_since_last_antibiotic` | int | Fill nulls with `age_days` |
| `cumulative_antibiotic_days` | int | Running count of antibiotic days per flock |
| `rolling_antibiotic_days_7d` | int | Antibiotic days in last 7 days (recency signal) |

All-zeros on the 5 one-hot columns = no antibiotic given (implicit "none"). Keep original `antibiotic_given` binary flag.

**Active windows** — carry forward a 1 for N days after administration:

| Drug | Window | Why |
|------|--------|-----|
| Enrofloxacin | 5 days | Standard course |
| Colistin | 5 days | Standard course |
| Amoxicillin | 5 days | Standard course |
| Doxycycline | 7 days | Longer half-life |
| Tylosin | 5 days | Standard course |

**Severity score** — validate empirically after engineering. If actual spike-rate-per-drug disagrees with the ranking, adjust the map.

Drop original `antibiotic_name` after deriving all features.

### 2. Ground Truth — Drop (Validation Only)

| Column | Missing % | Action | Why |
|--------|-----------|--------|-----|
| `disease_event_id` | ~85% | Drop | Ground truth — data leakage if used as feature |
| `suspected_disease` | ~85% | Drop | Same. Use only for post-hoc validation of predictions |

### 3. Weekly Measurements — Forward-Fill Within Flock

| Column | Missing % | Action | Why |
|--------|-----------|--------|-----|
| `litter_condition` | ~82% | Forward-fill per flock | Recorded weekly, condition persists between checks |
| `avg_weight_g` | ~83% | **Forward-fill** per flock | See tradeoff below ⚠️ |

#### ⚠️ `avg_weight_g` Tradeoff — The Most Important Decision

| Method | Pro | Con |
|--------|-----|-----|
| **Interpolation** | Biologically accurate — birds grow continuously, no flat staircases | Requires **future** weighing value → impossible at inference time |
| **Forward-fill** | Replicable in production — only uses past data | Creates flat steps between weekly weighings |

**Decision: Forward-fill.**  
**Why**: This is a production early-warning system, not a research paper. Interpolation causes **training-serving skew** — the model trains on data it will never see in deployment. Forward-fill is the only strategy that works identically in training and at inference time on a live farm.

### 4. Daily Operational Measurements — Forward-Fill Within Flock

| Column | Missing % | Action | Why |
|--------|-----------|--------|-----|
| `feed_consumed_kg` | 1.57% | Forward-fill per flock | Yesterday's consumption as proxy. Production-safe. |
| `feed_per_bird_g` | 1.57% | Forward-fill per flock | Derived from `feed_consumed_kg` — same root cause |
| `water_consumed_L` | 3.52% | Forward-fill per flock | Same logic. Water drops before spikes — preserving last known value is safest |

### 5. Equipment-Dependent — Fill by House Type

| Column | Missing % | Action | Why |
|--------|-----------|--------|-----|
| `co2_ppm` | ~87% | Fill **-1** + add `has_co2_sensor` flag | Only tunnel houses have CO2 sensors. 0 is misleading (ambient CO2 ≈ 400ppm). -1 is a clean sentinel for tree models |
| `fan_runtime_hours` | ~29% | Fill 0 + add `has_fan` flag | Open-sided houses have no fans |
| `cooling_pad_status` | ~29% | Fill "none" + add `has_cooling` flag | Same — open-sided houses |
| `ammonia_ppm` | ~57% | Fill 0 + add `has_ammonia_sensor` flag | Sensor-dependent. Can also try median imputation within house type |

### 6. Historical Features — Median + Flag

| Column | Missing % | Action | Why |
|--------|-----------|--------|-----|
| `prev_cycle_mortality_pct` | ~7.9% | Fill **median** + add `is_first_cycle` flag | See tradeoff below |
| `prev_cycle_fcr` | ~8.9% | Fill **median** + add `is_first_cycle` flag | Same logic |

> **Production note**: Compute median from **training set only**. Store as a pipeline constant. Never recompute at inference time.

#### Why Median, Not Zero?
Zero mortality / zero FCR is an **impossible outlier** — no real flock achieves that. Filling with 0 tells the model "first-cycle houses had perfect history," which is false and biases predictions. Median is a neutral, plausible placeholder. The `is_first_cycle` flag (derived from `cycle_number == 1`) lets the model learn to discount the fill.

### 7. Other

| Column | Missing % | Action | Why |
|--------|-----------|--------|-----|
| `days_since_last_vaccine` | 1.62% | Fill with `age_days` (no vaccine yet) | Before first vaccine, days_since = bird's age |
| `days_since_feed_delivery` | small | Forward-fill per flock | Delivery date persists until next delivery |

---

## Final Summary

| Category | Columns | Strategy |
|----------|---------|----------|
| **Sparse events** | antibiotic_name, vaccine_given, vaccine_route, scheduled_vaccine_today | Derive features → drop originals |
| **Ground truth** | disease_event_id, suspected_disease | Drop (validation only) |
| **Weekly measures** | litter_condition, avg_weight_g | Forward-fill within flock (first check = Day 1, no cold start) |
| **Daily operational** | feed_consumed_kg, feed_per_bird_g, water_consumed_L | Forward-fill within flock |
| **Equipment-dependent** | co2_ppm, fan_runtime_hours, cooling_pad_status, ammonia_ppm | Fill -1/0/none + equipment flag |
| **Historical** | prev_cycle_mortality_pct, prev_cycle_fcr | Median (training set only) + `is_first_cycle` flag |
| **Minor gaps** | days_since_last_vaccine, days_since_feed_delivery | Context-appropriate fill |

**Key principle**: Every fill strategy must be reproducible at inference time. If it needs future data, it's wrong for production.
