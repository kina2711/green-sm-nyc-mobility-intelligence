{{ config(materialized='table') }}

select
    md5(concat_ws('|', cast(pickup_month as varchar), operator)) as fare_grain_key,
    pickup_month,
    operator,
    service_category,
    count(*) as completed_trips,
    sum(fare_amount) filter (where fare_amount is not null) as observed_fare,
    count(fare_amount) as fare_trip_count,
    sum(trip_miles) filter (where trip_miles > 0) as paid_miles,
    sum(fare_amount) / nullif(count(fare_amount), 0) as avg_observed_fare,
    sum(fare_amount) / nullif(sum(trip_miles) filter (where trip_miles > 0), 0) as fare_per_paid_mile,
    sum(total_amount) / nullif(count(total_amount), 0) as avg_observed_total
from {{ ref('fct_trips') }}
group by pickup_month, operator, service_category
