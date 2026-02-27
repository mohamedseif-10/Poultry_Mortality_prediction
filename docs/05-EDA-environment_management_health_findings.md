# Environment, Management & Health — Findings, Decisions & Tradeoffs

## Key Insights at a Glance

| # | Finding | Effect | Action |
|---|---------|--------|--------|
| 1 | **House type is the strongest structural predictor** — open-sided houses have 2.4× the spike rate of tunnel-ventilated | **+23 pp** spike rate (open vs tunnel) | Keep `house_type` |
| 2 | **Litter condition is a valid but modest predictor (Simpson's paradox resolved)** — naive chart shows good > wet; age-controlled analysis reverses it | **+5.6 pp** (wet vs good, age-controlled) | Keep `litter_condition`, forward-fill weekly gaps |
| 3 | **Temperature is the dominant environmental driver** — spike-day inside temps shift ~3°C higher; aligns with summer mortality crisis | Clear distribution shift | Keep `temp_inside_avg_c`, engineer `temp_deviation` |
| 4 | **Feed & water consumption are age-confounded** — dramatic spike/no-spike differences vanish once you account for age (young birds eat/drink less AND die more) | Confounded | Keep raw features; trees handle the interaction |
| 5 | **Vaccination stress is real but brief** — spike rate +5 pp on vaccine days (first 2 weeks overlap) | **+5 pp** | Engineer `days_since_last_vaccine` |
| 6 | **Antibiotics are reactive, not preventive** — spike rate nearly identical with/without antibiotics (9% of days) | ~0 pp | Keep `antibiotic_given` as reactive signal |
| 7 | **Farm-level variation is large** — worst farm 42.7% spike rate vs best 17.0% (2.5× ratio) | **25 pp** spread | Keep `farm_id` |

---

## 1. Environmental Analysis

### 1.1 Temperature Deviation (Inside vs Target)

The house temperature deviation (actual − target-for-age) is centered near 0°C but **right-skewed** — positive deviations (houses running hot) are more common and extend to +20°C, while negative deviations rarely exceed −15°C.

**Senior insight:** This asymmetry reflects the reality of Egyptian poultry farming — cooling capacity (evaporative pads, fans) is the bottleneck. Heating is easier and cheaper. The right tail represents summer days where ventilation cannot keep up with ambient heat, directly linking to the summer mortality crisis documented in doc 04.

### 1.2 Environmental Features by Spike Status

Overlaid density plots of spike vs no-spike distributions reveal clear separation for some features:

| Feature | Spike Shift | Interpretation |
|---------|------------|----------------|
| `temp_inside_avg_c` | **Rightward** (~3°C higher) | Heat stress is the #1 driver — consistent with summer findings |
| `humidity_inside_pct` | **Rightward** (higher humidity) | High humidity compounds heat stress (evaporative cooling fails) |
| `ammonia_ppm` | **Rightward** (higher ammonia) | Ammonia damages respiratory epithelium; threshold harm >20 ppm |
| `temp_outside_avg_c` | **Rightward** (hotter outside) | Confirms the season/heat link is not just a temporal artifact |

**Key takeaway:** Temperature + humidity form the dominant environmental risk cluster. Ammonia contributes but overlaps more between spike and non-spike, suggesting it's a secondary factor that compounds thermal stress.

### 1.3 Temperature Range (Daily Max − Min)

Daily temperature swings average ~7°C (range 4–10°C). However, the box plot shows **no meaningful difference** between spike and non-spike days — both have median ~7°C with identical IQR.

**Decision:** Do not engineer `temp_range` as a standalone feature — it carries negligible signal. The average inside temperature is the better predictor. Temperature range could still matter for very young birds (<7d), but the aggregate signal is too weak.

### Environmental Feature Decisions

| Feature | Action | Reason |
|---------|--------|--------|
| `temp_inside_avg_c` | **Keep** | Strongest environmental predictor; clear spike separation |
| `humidity_inside_pct` | **Keep** | Compounds heat stress; visible right-shift on spike days |
| `ammonia_ppm` | **Keep** | Secondary signal; respiratory damage pathway |
| `temp_outside_avg_c` | **Keep** | Captures ambient conditions the house must fight against |
| `temp_deviation` | **Engineer** | `temp_inside_avg_c − target_temp_for_age_c` — captures house control quality |
| `temp_range` | **Do not create** | No spike/no-spike separation in box plot |

---

## 2. Farm, Breed & House Analysis

### 2.1 Breed Differences

| Breed | Spike Rate | Avg Daily Mortality % |
|-------|-----------|----------------------|
| Cobb_500 | **~32%** | ~0.40% |
| Hubbard | ~27% | ~0.38% |
| Ross_308 | ~26.5% | ~0.35% |

Cobb_500 shows ~5 pp higher spike rate and the highest average mortality. This is biologically plausible — Cobb_500 is selected for fast growth, which often comes at the cost of heat tolerance and metabolic resilience. Ross_308 is known for slightly better robustness.

**Caution:** Breed differences could be confounded with farm assignment (if certain farms only use certain breeds) or with season (if breed choices shifted over time). These aren't controlled here — tree models will learn the interaction naturally.

### 2.2 House Type — Strongest Structural Signal

| House Type | Spike Rate |
|-----------|-----------|
| **open_sided** | **~40%** |
| closed | ~25% |
| tunnel | **~17%** |

This is the **largest single structural predictor** found in this EDA. Open-sided houses lack environmental control — they're fully exposed to ambient temperature and humidity swings, exactly the conditions that drive the summer mortality crisis. Tunnel-ventilated houses maintain the tightest climate control with negative-pressure airflow.

**Senior insight:** In Egypt's climate, house type is arguably more important than breed choice. A mediocre breed in a tunnel house will outperform a superior breed in an open-sided shed during June–August. Industry studies in tropical/subtropical climates consistently show substantial mortality reductions (30–60%) when upgrading from passive to active environmental control.

### 2.3 Farm-Level Variation

| Metric | Value |
|--------|-------|
| Worst farm (FARM_005) | Spike rate **42.7%**, avg mortality 0.61% |
| Best farm (FARM_019) | Spike rate **~17%** |
| Mean | ~28% |
| Spread (worst − best) | **~25 pp** |

Top 5 worst farms: FARM_005 (42.7%), FARM_047 (39.2%), FARM_011 (38.7%), FARM_030 (34.9%), FARM_018 (34.9%).

The 2.5× ratio between worst and best farms reflects **management quality** — biosecurity practices, ventilation maintenance, stockmanship, disease response speed. Farm ID acts as a composite proxy for all these unmeasured management factors. Across 50 farms, the distribution is roughly normal around the mean, with 5–6 farms clearly in the tail.

### 2.4 Day-Old Chick (DOC) Quality & Transport

- **DOC quality score** (1–10): Peaks around 7, roughly normal. The spike vs non-spike density plots show **nearly identical distributions** — DOC quality has minimal discriminative power for same-day mortality spikes. This is expected: DOC quality affects first-week survival, but the effect is diluted when pooled across all ages.
- **DOC arrival temperature**: Shows a slight right tail for spike days (hotter transport → stress on chicks). However, this is a flock-level constant (same value every day of the cycle), not a dynamic predictor. Its signal may be captured by early-life mortality patterns.

### 2.5 Hatchery Supply Chain

All 5 hatcheries show nearly identical spike rates (~26–29%) and DOC quality scores (~7.0). **No hatchery stands out** as a quality outlier. This suggests the supply chain is homogeneous, or that any hatchery differences are washed out by downstream management.

**Decision:** `hatchery_id` can be kept but expect low feature importance.

### Farm/Breed/House Decisions

| Feature | Action | Reason |
|---------|--------|--------|
| `house_type` | **Keep (high priority)** | Strongest structural predictor: 23 pp spread |
| `farm_id` | **Keep** | 25 pp spread captures unmeasured management quality |
| `breed` | **Keep** | ~5 pp effect (Cobb_500 vs Ross_308); biologically plausible |
| `hatchery_id` | **Keep (low priority)** | Negligible variation (~3 pp spread); may be useful for interaction terms |
| `doc_quality_score` | **Keep** | Flock-level constant; minor signal for early-life vulnerability |
| `doc_arrival_temp_c` | **Keep** | Slight transport-stress signal; flock-level constant |

---

## 3. Feed, Water & Weight Analysis

### 3.1 Weight Growth Curve vs Hubbard Standard

Actual average flock weight tracks the Hubbard breed standard closely from day 1 (~40g) through day 30 (~1,400g). After day 35, **variance explodes** — the ±1 std dev band widens dramatically, with some flocks reaching 5,000g+ while others collapse below 500g.

| Metric | Value |
|--------|-------|
| Weighing days in dataset | 13,335 (17.9% of rows) |
| Weight range | 35g – 20,740g |
| Data quality issue | ~1% data entry errors (per data dictionary); max 20,740g is clearly erroneous for a ~40-day broiler |

**Senior insight:** The late-cycle variance explosion reflects (a) genuine divergence between well-managed and poorly-managed flocks, (b) weighing methodology inconsistency (not all birds are weighed), and (c) the known data entry errors. Weight-related features need outlier capping during feature engineering. The 20,740g max (~46 lbs) is physiologically impossible for any broiler — cap at the 99th percentile or ~5,000g to remove gross errors while preserving legitimate heavy-flock data.

### 3.2 Feed & Water Consumption by Age

- **Feed per bird:** Smooth sigmoid curve 15g (day 1) → ~175g (day 40). This is textbook broiler nutrition — no anomalies.
- **Water consumed:** Near-linear increase from ~500L to ~7,000L by day 40 (total house consumption scales with flock size and bird mass).
- **Feed phase transitions:** Clean transitions visible — starter (~day 1–10), grower (~day 10–25), finisher (~day 25–35), withdrawal (~day 35+). Transition points are well-defined without major overlap.

### 3.3 Water-to-Feed Ratio (W:F)

| Metric | Value |
|--------|-------|
| Median ratio | ~2.0 L/kg |
| Distribution | Normal-ish, range ~1.0–3.0 |
| Spike days | Slight leftward shift (lower ratio) |

A dropping W:F ratio is a classic early-warning indicator in poultry — birds reduce water intake before clinical signs appear. The distribution overlap between spike and no-spike is substantial, so the signal is weak in isolation, but it's a well-established domain feature.

### Feed/Water/Weight Decisions

| Feature | Action | Reason |
|---------|--------|--------|
| `feed_per_bird_g` | **Keep** | Strong age proxy with independent nutritional signal |
| `water_consumed_L` | **Keep** | House-level consumption; scales with flock health |
| `avg_weight_g` | **Keep (with outlier capping)** | Cap at 99th percentile or ~5,000g to remove gross entry errors; only 17.9% of days have weighing |
| `feed_phase` | **Keep** | Clean categorical; encodes lifecycle stage |
| `water_feed_ratio` | **Engineer** | `water_consumed_L / feed_consumed_kg` — early-warning signal per domain knowledge |
| `weight_vs_standard` | **Consider engineering** | `avg_weight_g / hubbard_standard_weight_g` — deviation from expected growth |

> **Important confound warning:** Feed per bird and water consumption both have large spike/no-spike differences in naive box plots because spike days concentrate in early life (age 0–10d) when consumption is lowest. This is the **same age confounding** as litter condition. Tree models handle this because they see `age_days`, but linear models would need explicit interaction terms.

---

## 4. Health Events & Vaccination

### 4.1 Vaccination Patterns

**Vaccine types given** (5 vaccines, roughly equal counts ~1,800 each):
- Mareks (day 1, injection)
- Newcastle_booster (drinking water)
- Newcastle_IB_final (spray)
- Gumboro_IBD (drinking water)
- Newcastle_IB_H120 (drinking water)

**Vaccine routes:** drinking_water (~5,200), injection (~1,800), spray (~1,800).

**Compliance:** 9,525 vaccines scheduled vs 9,055 actually given = **95.1% compliance rate**. This is strong compliance for Egyptian poultry operations.

### 4.2 Vaccination Stress Effect

| Metric | Non-Vaccine Days | Vaccine Days | Delta |
|--------|-----------------|-------------|-------|
| Spike rate | ~27% | ~32% | **+5 pp** |

The +5 pp spike rate on vaccine days is likely a **timing confound**, not a causal effect. Vaccines are concentrated in the first 14 days of life (Mareks day 1, Newcastle/Gumboro days 7–14), which overlaps with the high early-life mortality window. The stress of vaccination handling is brief and minor compared to the background biological mortality of young chicks.

**Decision:** Do not create `is_vaccine_day` — it's confounded with age. Instead, keep `days_since_last_vaccine` which captures the temporal distance from vaccination stress and has more utility for the model.

### 4.3 Antibiotic Usage

| Metric | Value |
|--------|-------|
| Days with antibiotic | 9.0% of all days |
| Days without | 91.0% |
| Spike rate (no antibiotic) | ~27% |
| Spike rate (with antibiotic) | ~29% |

**Antibiotic types used** (roughly equal counts ~1,200–1,500 each): Enrofloxacin, Tylosin, Doxycycline, Amoxicillin, Colistin.

**Senior insight:** The near-identical spike rates confirm that antibiotics are **prescribed reactively** — they're given *after* mortality starts rising, not prophylactically. This makes `antibiotic_given` a **concurrent/lagging indicator**, not a leading predictor. The model should learn this naturally — the feature captures "the farm recognized a problem and started treatment," which is informative but doesn't predict future spikes. Be careful about target leakage if the antibiotics are started on the same day as the spike.

### 4.4 Litter Condition — Simpson's Paradox Deep Dive

#### The Paradox

Naive bar chart shows **good litter has the highest spike rate** — the opposite of biological expectation (wet litter → ammonia → respiratory disease).

| Litter (naive) | Spike Rate | Avg Mortality % |
|----------------|-----------|----------------|
| Good | **41.7%** | 0.59% |
| Moderate | 30.3% | 0.44% |
| Wet | 25.3% | 0.31% |

#### Root Cause: Age Confounding

Litter starts fresh ("good") at flock placement and degrades over time. "Good" litter is therefore heavily concentrated in the first 10 days — the exact window where early-life mortality peaks.

| Litter | Median Age | % Rows ≤ 10 Days |
|--------|-----------|-------------------|
| Good | 14 days | **37.9%** |
| Moderate | 28 days | 21.9% |
| Wet | 28 days | 9.6% |

#### Age-Controlled Results (age > 10 days only)

| Litter | Spike Rate | Avg Mortality % |
|--------|-----------|----------------|
| Good | **12.4%** | 0.212% |
| Moderate | 13.3% | 0.224% |
| Wet | **18.0%** | 0.250% |

**Pattern reverses completely.** Once the first-week mortality crash is removed, wet litter has the highest spike rate — consistent with the ammonia/disease pathway.

#### Forward-Fill + Age-Segment Stratification

Litter condition is recorded weekly (~82% of rows are NaN). After forward-filling within each flock:

| Age Segment | Good | Moderate | Wet | Expected Order? |
|-------------|------|----------|-----|-----------------|
| 0–7d | 88.4 | 90.0 | 93.5 | ✓ (all near ceiling) |
| 8–14d | 25.0 | 28.6 | **37.0** | ✓ **(strongest signal)** |
| 15–21d | 9.8 | 11.7 | 11.0 | ✗ (~noise, 0.7 pp) |
| 22–28d | 7.9 | 9.2 | 11.8 | ✓ |
| 29–35d | 11.5 | 11.3 | 12.6 | ✗ (~noise, 0.2 pp) |
| 36+d | 11.0 | 11.2 | 11.8 | ✓ |

**Result:** 4/6 age segments show the expected gradient (wet > moderate > good). The two "failures" (15–21d, 29–35d) differ by less than 1 pp — well within sampling noise.

**Senior insight:** The litter effect is real but **modest** (2–5 pp within age segments). This is typical for poultry — litter quality is a secondary risk factor subordinate to age, temperature, and housing. The 8–14d segment shows the clearest signal (12 pp gap) because chicks in this window are past the first-week crash but still immunologically immature and vulnerable to respiratory irritants from ammonia buildup.

#### Litter Decisions

| Feature | Action | Reason |
|---------|--------|--------|
| `litter_condition` | **Keep** | Real signal once age is controlled; forward-fill during feature engineering |
| Forward-fill | **Apply during FE** | Fill NaN gaps by carrying last observation forward within each flock (biologically sound — litter degrades gradually) |
| Interaction term | **Not needed** | Tree models see `age_days` alongside litter and learn the interaction |

---

## 5. Disease Ground Truth (Validation Only)

> **These columns are NOT for modeling.** Disease labels (`disease_event_id`, `suspected_disease`) represent simulated ground truth. Using them as features would be target leakage.

### What the Ground Truth Tells Us

| Metric | Value |
|--------|-------|
| Days with active disease | 6,859 (9.2%) |
| Unique disease events | 5 |

**Disease types and spike rates:**

| Disease | Days Active | Spike Rate |
|---------|------------|-----------|
| Newcastle | ~900 | **~99%** |
| Gumboro | ~600 | **~87%** |
| Heat_Stress | ~5,300 | **~56%** |
| None | ~67,500 | ~24% |

**Key observations:**
- **Heat_Stress dominates** — 77% of disease-event days. This validates the summer mortality crisis finding from doc 04.
- **Newcastle near-100% spike rate** — consistent with this being one of the most devastating poultry diseases, with rapid and severe mortality.
- **Gumboro ~87%** — immunosuppressive disease (targets the bursa of Fabricius) that peaks in weeks 3–6, aligning with the early-life vulnerability window.
- **Baseline (no disease) ~24%** — this is the "normal" spike rate driven by early-life mortality and routine management variation.

### Sample Flock Disease Windows

Individual flock mortality curves show disease events (shaded in red) aligning cleanly with mortality peaks — confirming the disease labels are well-simulated and temporally consistent.

---

## 6. Historical Features & Stocking Density

### 6.1 Previous Cycle Performance

| Feature | Distribution | Missing |
|---------|-------------|---------|
| `prev_cycle_mortality_pct` | Right-skewed, most 5–20%, tail to 70% | 7.9% (expected: first cycle of each house) |
| `prev_cycle_fcr` | Normal, peaked at 2.3–2.5 | Same |

The spike vs non-spike comparison for previous-cycle mortality shows a **slight rightward shift for spike days** — houses that had bad outcomes last cycle are marginally more likely to spike this cycle. This could reflect persistent environmental problems (poor ventilation, structural issues, disease carryover in litter).

**Decision:** Keep `prev_cycle_mortality_pct` and `prev_cycle_fcr` — they capture house-level "memory" that may help the model. Missing values (first cycles) should be imputed with the dataset median.

### 6.2 Stocking Density

| Metric | Value |
|--------|-------|
| Range | 12–20 birds/m² |
| Peak | 15–18 birds/m² |

The stocking density distributions for spike vs no-spike **overlap almost completely** — no clear separation. This is surprising given that overcrowding is a known mortality risk factor. Possible explanations:
1. The dataset's density range (12–20) is relatively narrow — all farms operate within Egyptian regulatory/industry norms.
2. Density effects may only emerge at extremes (>22+ birds/m²), which aren't present.
3. Density's effect may be mediated through temperature/ammonia (captured by other features).

**Spike rate by house total cycles** shows a noisy pattern with no clear trend — new and experienced houses perform similarly.

### Historical/Density Decisions

| Feature | Action | Reason |
|---------|--------|--------|
| `prev_cycle_mortality_pct` | **Keep** | Slight predictive signal; captures house "memory" |
| `prev_cycle_fcr` | **Keep** | Feed conversion ratio as house-quality proxy |
| `stocking_density_per_m2` | **Keep (low priority)** | Weak standalone signal but may interact with temp/humidity |
| `house_total_cycles` | **Keep** | No clear trend, but low cost to include |
| `placement_count` | **Keep** | Flock size; scales with heat load and management workload |

---

## 7. Key Pairwise Feature Relationships

### Box Plot Overview (10 Features × Spike/No-Spike)

| Feature | Spike vs No-Spike Separation | Note |
|---------|------------------------------|------|
| `feed_per_bird_g` | **Large** (spike median ~75g vs no-spike ~125g) | **Age confound** — spike days = young birds = less feed |
| `water_consumed_L` | **Large** (spike median ~2000L vs no-spike ~5500L) | **Age confound** — same mechanism as feed |
| `temp_inside_avg_c` | **Moderate** (spike ~30°C vs no-spike ~27°C) | **Genuine signal** — direct heat stress pathway |
| `humidity_inside_pct` | **Weak** (similar medians ~63%) | Slight right tail for spikes |
| `ammonia_ppm` | **Weak–Moderate** (spike slightly higher) | Secondary environmental factor |
| `power_outage_hours` | **Negligible** (both near 0) | Rare event; insufficient data to assess |
| `worker_count` | **Weak** (spike slightly lower ~5 vs ~6) | Consistent with Friday/holiday findings |
| `days_since_last_vaccine` | **Negligible** (similar distributions) | Vaccination timing not predictive |
| `doc_quality_score` | **Negligible** (both ~7 median) | Flock-level constant; no same-day signal |
| `stocking_density_per_m2` | **Negligible** (near-identical) | Narrow range in this dataset |

**Critical warning:** The two features showing the largest naive separation (feed and water) are **entirely age-confounded**. They will show high feature importance in a naive model but for wrong reasons. Tree models mitigate this because they condition on `age_days`, but any stakeholder presentation must note this caveat.

---

## 8. Consolidated Modeling Decisions

### Tier 1 — High-Priority Features (strong, validated signal)

| Feature | Signal Strength | Key Evidence |
|---------|----------------|-------------|
| `house_type` | **Very strong** | 23 pp spread (open_sided vs tunnel) |
| `temp_inside_avg_c` | **Strong** | Clear distribution shift on spike days |
| `age_days` | **Dominant** | Drives most univariate patterns; 88–94% spike rate at 0–7d |
| `farm_id` | **Strong** | 25 pp spread across 50 farms |
| `breed` | **Moderate** | ~5 pp (Cobb_500 vs Ross_308) |

### Tier 2 — Moderate-Priority Features (real but modest signal)

| Feature | Signal Strength | Key Evidence |
|---------|----------------|-------------|
| `humidity_inside_pct` | **Moderate** | Compounds heat stress |
| `ammonia_ppm` | **Moderate** | Respiratory pathway; right-shifted on spike days |
| `litter_condition` | **Moderate** | +5.6 pp (wet vs good) after age control; forward-fill required |
| `feed_per_bird_g` | **Moderate** | Confounded with age but carries independent nutritional signal |
| `water_consumed_L` | **Moderate** | Same confound caveat |
| `antibiotic_given` | **Moderate** | Reactive signal — "treatment started" indicator |
| `prev_cycle_mortality_pct` | **Moderate** | House-level "memory" |

### Tier 3 — Low-Priority Features (keep but expect low importance)

| Feature | Reason to Keep |
|---------|---------------|
| `hatchery_id` | Negligible variation, but zero cost to include |
| `doc_quality_score` | Flock-level constant; may help early-life predictions |
| `doc_arrival_temp_c` | Transport stress proxy |
| `stocking_density_per_m2` | May interact with temp/humidity |
| `house_total_cycles` | No trend, but no cost |
| `prev_cycle_fcr` | House-quality proxy |

### Features to Engineer

| Feature | Formula | Rationale |
|---------|---------|-----------|
| `temp_deviation` | `temp_inside_avg_c − target_temp_for_age_c` | House control quality (how far from optimal?) |
| `water_feed_ratio` | `water_consumed_L / feed_consumed_kg` | Early-warning signal per domain knowledge |
| `weight_vs_standard` | `avg_weight_g / hubbard_standard_weight_g` | Growth deviation — underweight = stressed flock |
| `litter_condition_ffill` | Forward-fill within flock | Fills weekly gaps (82% NaN → 0% — 100% coverage achieved) |

### Features NOT to Create

| Feature | Reason |
|---------|--------|
| `temp_range` | No spike separation in box plot |
| `is_vaccine_day` | Age confounded; use `days_since_last_vaccine` instead |

### Data Quality Actions (Feature Engineering Phase)

| Issue | Action |
|-------|--------|
| `avg_weight_g` max = 20,740g | Cap at 99th percentile or ~5,000g (flock averages above 5 kg are physiologically impossible; 3,000–3,500g is typical at day 40 but top-performing male-heavy flocks in extended cycles can legitimately exceed 3,500g) |
| `litter_condition` 82% NaN | Forward-fill within flock — achieves 100% coverage (every flock has at least one observation before forward-fill carries it) |
| `prev_cycle_mortality_pct` 7.9% NaN | Impute with dataset median (first cycle houses) |
| Weighing days = 17.9% | Accept sparsity; weight features are only available on weigh days |

---

## 9. Open Investigations

| # | Item | Status |
|---|------|--------|
| 1 | Breed × house_type interaction — does the Cobb_500 penalty disappear in tunnel houses? | Not yet checked |
| 2 | Farm_id leakage risk — if train/test split isn't farm-aware, farm_id may overfit | Address in modeling pipeline |
| 3 | Power outage signal — too few events for univariate analysis; may emerge in multivariate model | Monitor during modeling |
| 4 | Antibiotic timing — does antibiotic start *before* or *after* spike onset? Need flock-level lag analysis | Not yet checked |
