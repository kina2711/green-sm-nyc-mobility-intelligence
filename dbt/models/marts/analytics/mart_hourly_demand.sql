{{ config(materialized='table') }}

select
    md5(concat_ws('|', cast(pickup_zone_id as varchar),
        cast(pickup_day_of_week as varchar), cast(pickup_hour as varchar))) as demand_grain_key,
    pickup_zone_id as zone_id,
    pickup_day_of_week as day_of_week,
    pickup_hour,
    count(*) as completed_trips,
    count(distinct date_key) as observed_days,
    count(*)::double / nullif(count(distinct date_key), 0) as avg_completed_trips_per_observed_day,
    sum(fare_amount) / nullif(count(fare_amount), 0) as avg_observed_fare
from {{ ref('fct_trips') }}
group by pickup_zone_id, pickup_day_of_week, pickup_hour
