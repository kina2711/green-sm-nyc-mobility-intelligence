{{ config(materialized='table') }}

with aggregated as (
    select
        trips.pickup_month,
        zones.borough,
        trips.operator,
        trips.service_category,
        count(*) as completed_trips,
        sum(trips.fare_amount) filter (where trips.fare_amount is not null) as observed_fare,
        count(trips.fare_amount) as fare_trip_count,
        sum(trips.trip_miles) filter (where trips.trip_miles > 0) as paid_miles
    from {{ ref('fct_trips') }} as trips
    inner join {{ ref('dim_zone') }} as zones
        on trips.pickup_zone_id = zones.zone_id
    group by trips.pickup_month, zones.borough, trips.operator, trips.service_category
)

select
    md5(concat_ws('|', cast(pickup_month as varchar), borough, operator)) as market_grain_key,
    pickup_month,
    borough,
    operator,
    service_category,
    completed_trips,
    observed_fare,
    fare_trip_count,
    paid_miles,
    observed_fare / nullif(fare_trip_count, 0) as avg_observed_fare,
    observed_fare / nullif(paid_miles, 0) as fare_per_paid_mile,
    completed_trips::double
        / sum(completed_trips) over (partition by pickup_month, borough) as completed_trip_share
from aggregated
