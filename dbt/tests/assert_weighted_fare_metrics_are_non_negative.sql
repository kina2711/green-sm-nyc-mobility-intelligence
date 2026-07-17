select fare_grain_key, avg_observed_fare, fare_per_paid_mile
from {{ ref('mart_fare_positioning') }}
where avg_observed_fare < 0 or fare_per_paid_mile < 0

