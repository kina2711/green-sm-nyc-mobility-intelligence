select
    pickup_month,
    borough,
    sum(completed_trip_share) as total_share
from {{ ref('mart_market_overview') }}
group by pickup_month, borough
having abs(sum(completed_trip_share) - 1.0) > 0.000001
