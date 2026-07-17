with unioned as (
    select * from {{ ref('stg_tlc__yellow_trips') }}
    union all by name
    select * from {{ ref('stg_tlc__fhvhv_trips') }}
)

select
    *,
    cast(pickup_at as date) as pickup_date,
    date_trunc('month', pickup_at)::date as pickup_month,
    extract('year' from pickup_at)::integer as pickup_year,
    extract('dow' from pickup_at)::integer as pickup_day_of_week,
    extract('hour' from pickup_at)::integer as pickup_hour,
    case
        when trip_minutes > 0 then trip_miles / (trip_minutes / 60.0)
    end as speed_mph,
    case
        when trip_miles > 0 then fare_amount / trip_miles
    end as fare_per_mile,
    pickup_zone_id in (1, 132, 138) or dropoff_zone_id in (1, 132, 138) as is_airport_trip
from unioned

