{{ config(materialized='table') }}

with operator_year as (
    select pickup_year, operator, count(*) as completed_trips
    from {{ ref('fct_trips') }}
    group by pickup_year, operator
),

shares as (
    select
        pickup_year,
        operator,
        completed_trips,
        completed_trips::double / sum(completed_trips) over (partition by pickup_year) as share
    from operator_year
)

select
    pickup_year,
    round(sum(share * share) * 10000, 0) as completed_trip_hhi,
    sum(completed_trips) as completed_trips
from shares
group by pickup_year
