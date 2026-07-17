select
    pickup_zone_id as zone_id,
    pickup_year,
    count(*) as completed_trips,
    sum(fare_amount) filter (where fare_amount is not null) as observed_fare,
    count(fare_amount) as fare_trip_count,
    sum(case when is_airport_trip then 1 else 0 end) as airport_trips
from {{ ref('int_trips_conformed') }}
group by pickup_zone_id, pickup_year
