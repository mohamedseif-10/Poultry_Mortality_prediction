# Identity
identities = [
    "flock_id",
    "farm_id",
    "house_id",
    "cycle_number",
    "date",
    "age_days"
]


# Flock Metadata
flock_metadata = [
    "breed",
    "placement_count",
    "house_type",
    "governorate",
    "stocking_density_per_m2",
    "house_area_m2",
    "doc_quality_score",
    "doc_arrival_temp_c",
    "hatchery_id",
    "feed_batch_id",
    "days_since_feed_delivery",
    "current_flock_size",
    "house_total_cycles"
]


# Weight
weight_features = [
    "avg_weight_g",
    "weighing_done",
    "hubbard_standard_weight_g"
]


# Feed
feed_features = [
    "feed_consumed_kg",
    "feed_per_bird_g",
    "feed_phase"
]


# Water
water_features = [
    "water_consumed_L"
]


# Inside Environment
inside_environment = [
    "temp_inside_min_c",
    "temp_inside_max_c",
    "temp_inside_avg_c",
    "target_temp_for_age_c",
    "humidity_inside_pct",
    "ammonia_ppm",
    "co2_ppm",
    "fan_runtime_hours",
    "cooling_pad_status",
    "power_outage_hours"
]


# Outside Environment
outside_environment = [
    "temp_outside_avg_c",
    "humidity_outside_pct",
    "wind_speed_kmh",
    "khamaseen_dust_storm"
]


# Calendar
calendar_features = [
    "month",
    "day_of_week",
    "season",
    "is_holiday",
    "is_ramadan"
]


# Health Events
health_events = [
    "vaccine_given",
    "vaccine_route",
    "scheduled_vaccine_today",
    "days_since_last_vaccine",
    "antibiotic_given",
    "antibiotic_name",
    "vitamin_supplement_given",
    "litter_condition",
    "worker_count"
]


# Disease Ground Truth
disease_ground_truth = [
    "disease_event_id",
    "suspected_disease"
]


# Historical (Previous Cycle)
historical_features = [
    "prev_cycle_mortality_pct",
    "prev_cycle_fcr"
]



# Targets
targets = [
    "daily_deaths",
    "daily_culls",
    "cumulative_deaths",
    "cumulative_culls",
    "daily_mortality_pct",
    "cumulative_mortality_pct",
    "mortality_spike"
]

# I think I will make different pipelines for different feature groups, and then combine them later on.
FEATURE_GROUPS = {
    "identities": identities,
    "flock_metadata": flock_metadata,
    "targets": targets,
    "weight": weight_features,
    "feed": feed_features,
    "water": water_features,
    "inside_environment": inside_environment,
    "outside_environment": outside_environment,
    "calendar": calendar_features,
    "health_events": health_events,
    "disease_ground_truth": disease_ground_truth,
    "historical_features": historical_features
}