{{ config(materialized='view') }}

select
    trips.trip_id,
    md5(concat_ws('|', trips.service_type, trips.operator)) as service_key,
    trips.pickup_date as date_key,
    trips.pickup_zone_id,
    trips.dropoff_zone_id,
    trips.service_type,
    trips.operator,
    trips.service_category,
    trips.pickup_at,
    trips.dropoff_at,
    trips.pickup_month,
    trips.pickup_year,
    trips.pickup_day_of_week,
    trips.pickup_hour,
    trips.trip_miles,
    trips.trip_minutes,
    trips.speed_mph,
    trips.fare_amount,
    trips.total_amount,
    trips.driver_pay,
    trips.fare_per_mile,
    trips.is_airport_trip
from {{ ref('int_trips_conformed') }} as trips

