# Data Dictionary

74,354 rows × 65 columns | 50 farms | 150 houses | 1,905 flocks | Jan 2023 – Dec 2024

One row = one day in one flock's cycle.

---

## Identity (6 Columns)

| Column | Type | Description |
|---|---|---|
| flock_id | str | Unique flock identifier (e.g. FARM_001_H1_C03) |
| farm_id | str | Farm identifier |
| house_id | str | House/shed identifier |
| cycle_number | int | Which cycle number this house is on |
| date | str | Date (YYYY-MM-DD) |
| age_days | int | Bird age in days since placement (Day 1 = placement day) |

---

## Flock Metadata (13 Column)

| Column | Type | Description |
|---|---|---|
| breed | str | Hubbard (85%), Ross_308, Cobb_500 |
| placement_count | int | Number of DOC placed on Day 1 |
| house_type | str | open_sided / closed / tunnel |
| governorate | str | Farm location (mostly Bahareya) |
| stocking_density_per_m2 | float | Birds per m² (appropriate 15-20 in most cases)|
| house_area_m2 | int | House floor area |
| doc_quality_score | float | Day-old chick quality at arrival (1–10) |
| doc_arrival_temp_c | float | Temperature during DOC transport — stress indicator |
| hatchery_id | str | Which hatchery supplied the DOC, It is not a key. It is a characteristic of the flock to identify Supply chain quality differences. |
| feed_batch_id | str | Feed batch identifier — changes mid-cycle |
| days_since_feed_delivery | int | Feed freshness proxy |
| current_flock_size | int | Birds still alive today |
| house_total_cycles | int | How many cycles this house has run total |

---

## Targets (7 Columns)
### each one of them can be seperated problem and project!

| Column | Type | Description |
|---|---|---|
| daily_deaths | int | Birds found dead today |
| daily_culls | int | Sick birds actively removed today (underreported on Fridays/Ramadan) |
| cumulative_deaths | int | Total deaths from Day 1 to today |
| cumulative_culls | int | Total culls from Day 1 to today |
| daily_mortality_pct | float | daily_deaths / placement_count × 100 |
| cumulative_mortality_pct | float | cumulative_deaths / placement_count × 100 |
| **mortality_spike** | int | **1 if daily_mortality_pct > 0.30%, else 0 — main classification target** |

---

## Weight (3 Columns)
Weight is only recorded on weighing days (~weekly). Null on all other days — this is intentional and realistic.

| Column | Type | Description |
|---|---|---|
| avg_weight_g | float | Average flock weight (g) — null on non-weighing days, ~1% data entry errors |
| weighing_done | int | 1 if weight was recorded today, 0 otherwise |
| hubbard_standard_weight_g | int | Expected weight for this age per Hubbard breed standard |

---

## Feed (3 Columns) 
| Column | Type | Description |
|---|---|---|
| feed_consumed_kg | float | Total feed eaten by flock today (kg) — ~1.5% missing |
| feed_per_bird_g | float | feed_consumed_kg / flock_size × 1000 |
| feed_phase | str | starter / grower / finisher / withdrawal |

---

## Water (1 Column)
| Column | Type | Description |
|---|---|---|
| water_consumed_L | float | Total water consumed today (liters) — ~2% missing. Drops before mortality spikes. |

---

## Inside Environment (10 columns)

| Column | Type | Description |
|---|---|---|
| temp_inside_min_c | float | Minimum recorded temperature inside house |
| temp_inside_max_c | float | Maximum recorded temperature inside house |
| temp_inside_avg_c | float | Average temperature inside house |
| target_temp_for_age_c | float | What the temperature should be for this bird age |
| humidity_inside_pct | float | Relative humidity inside (%) |
| ammonia_ppm | float | Ammonia level (ppm) — null if no sensor (~57% missing) |
| co2_ppm | float | CO2 level (ppm) — tunnel houses only (~87% missing) |
| fan_runtime_hours | float | Hours fans ran today — null for open-sided houses |
| cooling_pad_status | str | working / partial / down / off — null for open-sided |
| power_outage_hours | float | Hours of power loss today (Egypt grid issues) |

---

## Outside Environment (Bahareya Oasis) (4 Columns)

| Column | Type | Description |
|---|---|---|
| temp_outside_avg_c | float | Outside temperature (Bahareya, not Cairo) |
| humidity_outside_pct | float | Outside relative humidity (%) |
| wind_speed_kmh | float | Wind speed — spikes during Khamaseen  |
| khamaseen_dust_storm | int | 1 if dust storm event today (April–May) |

---

## Calendar (5 Columns)

| Column | Type | Description |
|---|---|---|
| month | int | Month (1–12) |
| day_of_week | int | 0=Monday … 6=Sunday |
| season | str | winter / spring / summer / autumn |
| is_holiday | int | 1 if Friday or public holiday (affects worker behavior and reporting) |
| is_ramadan | int | 1 if during Ramadan |

---

## Health Events (9 Columns)

| Column | Type | Description |
|---|---|---|
| vaccine_given | str | Vaccine name if given today, else null|
| vaccine_route | str | spray / drinking_water / injection / eye_drop |
| scheduled_vaccine_today | str | What vaccine was supposed to be given today per program |
| days_since_last_vaccine | float | Days elapsed since last vaccine was administered |
| antibiotic_given | int | 1 if antibiotic administered today (I can use it to drive days_since_last_antibiotic) |
| antibiotic_name | str | Name of antibiotic given, else null |
| vitamin_supplement_given | int | 1 if vitamins/electrolytes given today |
| litter_condition | str | good / moderate / wet — recorded weekly only, null other days (So I can fill week days with the weekend value!) |
| worker_count | int | Number of workers on farm today (drops on holidays/Ramadan) |

---

## Disease Events (2 Columns)
These columns reveal the ground truth behind simulated outbreaks. In real data I would not have those so I will use them for understanding and validation only, not as model features!.

| Column | Type | Description |
|---|---|---|
| disease_event_id | str | Event name if flock is inside a simulated outbreak window, else null |
| suspected_disease | str | Newcastle / Gumboro / Heat_Stress — null if no active event |

---

## Historical (from previous cycle)
Null for the first cycle of each house — handle this in your pipeline.

| Column | Type | Description |
|---|---|---|
| prev_cycle_mortality_pct | float | Cumulative mortality % from previous cycle in this house |
| prev_cycle_fcr | float | FCR achieved in previous cycle in this house |

---

## Key Notes for Feature Engineering

- `avg_weight_g` and `hubbard_standard_weight_g` are both raw → I will compute deviation myself
- `feed_consumed_kg` and `water_consumed_L` are both raw → I will compute water-to-feed ratio myself
- `temp_inside_avg_c` and `target_temp_for_age_c` are both raw → I should compute deviation myself
- No lag features exist → So I need to build them (mortality lag1, lag2, lag3, rolling mean, etc.)
- No phase flags exist → derive from `age_days`
- No FCR-to-date exists → compute from cumulative feed and weight
- `disease_event_id` and `suspected_disease` are ground truth — do not use as features in your model

---