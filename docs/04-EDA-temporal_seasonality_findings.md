# Temporal & Seasonality Patterns — Findings, Decisions & Tradeoffs

## Key Insights at a Glance

| # | Finding | Effect | Action |
|---|---------|--------|--------|
| 1 | **Summer heat doubles mortality** — repeatable across 2023 & 2024. No age confounding. | **+11 pp** spike rate | Keep `month` |
| 2 | **Friday staffing drop is real** — fewer workers, culls drop 63%. Verified via cumulative accounting (not a recording artifact). | **+4 pp** spike rate | Keep `day_of_week` |
| 3 | **Holidays mirror Friday** — same mechanism (fewer workers → fewer culls). | **+4.8 pp** spike rate | Keep `is_holiday` |
| 4 | **Ramadan "protection" is a mirage** — Ramadan falls in Mar–Apr; month-controlled residual = −1.2 pp. | **~0 pp** | Drop `is_ramadan` |
| 5 | **Dataset edges are small-N artifacts** — 100% spike at start (3–5 flocks), collapse at end. | N/A | Flag with `is_ramp_up` |

---

## 1. Summer Mortality Crisis (Strongest Signal)

| Metric | Summer (Jun–Aug) | Winter (Dec–Feb) | Delta |
|--------|-----------------|------------------|-------|
| Avg daily mortality % | 0.631% | 0.305% | **+107%** (doubles, not triples) |
| Spike rate | 38.6% | 27.3% | **+11.3 pp** |
| Monthly peak | July ~49% | December ~19% | Largest single-month gap |

Two identical summer peaks (mid-2023, mid-2024) in both mortality % and total deaths — sustained multi-week trends, not outliers. Driven by heat stress: broilers can't sweat and rely on environmental cooling.

### Age × Season Confounding — Ruled Out

If summer flocks skewed younger, the seasonal peak would partly reflect early-life vulnerability (first 10 days are highest risk). Cross-tabulation shows **no confounding**:

| Period | Median Age | % Young (≤10d) |
|--------|-----------|----------------|
| **Summer** | **20** | **25.6%** |
| **Winter** | **20** | **26.5%** |
| **Difference** | **0** | **−0.9 pp** |

Flock age is uniform across months (Feb–Oct median = 20d). January is an outlier (median 16d, 33.1% young) — but that's the dataset ramp-up artifact, not a real placement pattern. **The summer crisis is genuine heat stress.** No interaction terms needed.

### Decision

| Feature | Action | Reason |
|---------|--------|--------|
| `month` | **Keep** | Strong, proven seasonal signal |
| `season` | **Keep for now** | Coarser grouping; evaluate redundancy post-modeling |
| `month_sin`/`month_cos` | **Engineer** | Cyclical encoding for linear models. Trees don't need this. |

> Do not create `is_summer` — it loses the June ramp-up and September ramp-down that `month` captures.

---

## 2. The Friday Effect (Real but Modest)

| Day | Spike Rate | Avg Culls | Avg Workers |
|-----|-----------|-----------|-------------|
| Mon–Thu | ~26–27% | ~15–16 | ~5.5 |
| **Friday** | **~31%** | **~6** | **~4** |
| Sat–Sun | ~27% | ~15–16 | ~5.5 |

Friday has fewer workers, far fewer culls, and a slightly higher spike rate. The pattern is consistent and clearly tied to reduced Friday staffing.

### Reporting Bias Verification

Used the accounting identity: `current_flock_size = placement_count − cumulative_deaths − cumulative_culls` (holds perfectly across all 74,354 rows). Derived implied daily culls from Δ cumulative:

| Day | Reported Culls | Implied Culls (Δ cumulative) | Gap |
|-----|---------------|------------------------------|-----|
| Mon–Thu | ~16.5 | ~15.0 | ~−1.6 |
| **Friday** | **6.1** | **5.5** | **−0.6** |
| Sat–Sun | ~16.6 | ~15.0 | ~−1.5 |

**The Friday cull drop is REAL.** Implied culls also drop to ~5.5 on Fridays — if culls were just not logged, the cumulative would still capture them. The ~1.5 gap across all days is a minor, uniform data quality issue (rounding/timing), not Friday-specific.

### Decision

| Feature | Action | Reason |
|---------|--------|--------|
| `day_of_week` | **Keep** | Captures Friday dip + any other weekly patterns |
| `is_friday` | **Do not create** | Redundant with `day_of_week`; modest effect (+4 pp) doesn't justify isolation |

---

## 3. Ramadan & Holiday Effects

### Holiday Effect

| Metric | Working Day | Holiday | Delta |
|--------|-------------|---------|-------|
| Spike rate | 26.7% | 31.5% | **+4.8 pp** |
| Avg daily culls | 16.8 | 6.1 | **−64%** |

Same mechanism as Friday: fewer workers → fewer proactive culls → higher spike rate.

### Ramadan Effect — Seasonal Confound

| Metric | Not Ramadan | Ramadan | Delta |
|--------|-------------|---------|-------|
| Spike rate (naive) | 27.9% | 22.9% | −5.1 pp |
| Worker count | 5.25 | 4.79 | −0.46 |

The naive −5.1 pp looks like Ramadan is protective, but Ramadan in this dataset falls **entirely in March–April** (cooler months with inherently lower spike rates). After controlling for month:

| Comparison | Spike Rate |
|------------|------------|
| Ramadan days (Mar–Apr) | 22.9% |
| Non-Ramadan days in **same months** | 24.0% |
| **Month-controlled Ramadan effect** | **−1.2 pp (negligible)** |

### Decision

| Feature | Action | Reason |
|---------|--------|--------|
| `is_holiday` | **Keep** | Clear signal: culls −64%, spike rate +4.8 pp |
| `is_ramadan` | **Drop** | Apparent effect is seasonal confound. Residual = −1.2 pp; redundant with `month` |

---

## 4. Dataset Edge Effects

### Start (Jan 2023)

| Period | Active Flocks | Spike Rate |
|--------|--------------|------------|
| Jan 1–5 | 3–5 | 90–100% |
| Jan 15 | ~50 | ~60% |
| Feb 15 | ~100 | ~20% |

**Root cause:** Law of small numbers. With 3–5 flocks, a single spike flock produces extreme aggregated rates. Verified: 100% spike rate aligns exactly with days ≤ 5 active flocks.

### End (Dec 2024–Jan 2025)

Same artifact in reverse — active flocks drop toward zero (incomplete cycles, farms stop reporting). Both edges need the same treatment.

### January Aggregation Bias

January's high monthly spike rate (~34%) is partially inflated by the 2023 ramp-up. January 2024 alone (stable flock count) would likely show a more normal rate.

### Decision

| Approach | Action | Reason |
|----------|--------|--------|
| Exclude first 45 days | **No** | Too aggressive — valid flock-level data exists |
| Filter aggregated trends | **Yes** | Use `active_flocks ≥ 10` for network-wide metrics |
| Add ramp-up flag | **Yes** | `is_ramp_up = (date < "2023-02-15")` |
| Flag dataset end | **Yes** | Filter/flag last 30 days (Dec 2024+) |

> **Key principle:** These filters apply to **aggregated metrics only**. Individual flock-level rows are valid regardless of network-wide flock count. Never drop rows from the modeling dataset based on this.

---

## 5. Consolidated Modeling Decisions

### Keep

| Feature | Strength |
|---------|----------|
| `month` | **Strong** — +11 pp summer spike rate |
| `day_of_week` | **Moderate** — +4 pp Friday effect |
| `is_holiday` | **Moderate** — culls −64%, spike +4.8 pp |

### Drop

| Feature | Reason |
|---------|--------|
| `is_ramadan` | Seasonal confound; month-controlled residual = −1.2 pp |
| `is_friday` | Redundant with `day_of_week` |
| `is_summer` | Loses seasonal shape; `month` is better |

### Engineer

| Feature | Formula |
|---------|---------|
| `month_sin` / `month_cos` | `sin/cos(2π × month / 12)` — cyclical encoding for linear models |
| `is_ramp_up` | `date < "2023-02-15"` — flag unreliable early period |

### Aggregated Trend Filters (not modeling data)

| Filter | Rule |
|--------|------|
| Low-flock days | `active_flocks ≥ 10` |
| Tail end | `date < "2024-12-01"` |

---

## 6. Open Items

Items 1–4 resolved: Age × Season (no confounding ✅), Ramadan chart (fixed ✅), Friday reporting bias (disproven ✅), Ramadan × Month (confound confirmed, drop feature ✅).

**Remaining:**
- **January isolation** — Re-compute January spike rate using 2024 data only to check if the 2023 ramp-up artifact is inflating the monthly aggregate.
