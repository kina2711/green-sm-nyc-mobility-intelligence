{{ config(materialized='table') }}

with latest_year as (
    select max(pickup_year) as year from {{ ref('int_zone_yearly_metrics') }}
),

joined as (
    select
        current.zone_id,
        current.pickup_year as analysis_year,
        current.completed_trips,
        current.observed_fare / nullif(current.fare_trip_count, 0) as avg_observed_fare,
        current.airport_trips::double / nullif(current.completed_trips, 0) as airport_trip_share,
        prior.completed_trips as prior_year_completed_trips,
        (current.completed_trips - prior.completed_trips)::double
            / nullif(prior.completed_trips, 0) as yoy_completed_trip_growth
    from {{ ref('int_zone_yearly_metrics') }} as current
    inner join latest_year on current.pickup_year = latest_year.year
    left join {{ ref('int_zone_yearly_metrics') }} as prior
        on current.zone_id = prior.zone_id
       and current.pickup_year = prior.pickup_year + 1
),

scored as (
    select
        *,
        percent_rank() over (order by completed_trips) * 100 as activity_component,
        percent_rank() over (order by coalesce(yoy_completed_trip_growth, 0)) * 100 as growth_component,
        percent_rank() over (order by avg_observed_fare) * 100 as fare_component,
        percent_rank() over (order by airport_trip_share) * 100 as airport_component
    from joined
)

select
    scored.zone_id,
    zones.borough,
    zones.zone_name,
    scored.analysis_year,
    scored.completed_trips,
    scored.prior_year_completed_trips,
    scored.yoy_completed_trip_growth,
    scored.avg_observed_fare,
    scored.airport_trip_share,
    round(scored.activity_component, 2) as activity_component,
    round(scored.growth_component, 2) as growth_component,
    round(scored.fare_component, 2) as fare_component,
    round(scored.airport_component, 2) as airport_component,
    round(
        0.35 * scored.activity_component
        + 0.30 * scored.growth_component
        + 0.20 * scored.fare_component
        + 0.15 * scored.airport_component,
        2
    ) as opportunity_score
from scored
inner join {{ ref('dim_zone') }} as zones
    on scored.zone_id = zones.zone_id

