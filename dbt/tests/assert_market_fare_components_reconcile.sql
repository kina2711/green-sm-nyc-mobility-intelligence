select *
from {{ ref('mart_market_overview') }}
where abs(avg_observed_fare - observed_fare / nullif(fare_trip_count, 0)) > 0.000001
   or abs(fare_per_paid_mile - observed_fare / nullif(paid_miles, 0)) > 0.000001
