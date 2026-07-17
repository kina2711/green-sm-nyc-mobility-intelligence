{{ config(materialized='table') }}

with bounds as (
    select min(pickup_date) as min_date, max(pickup_date) as max_date
    from {{ ref('int_trips_conformed') }}
),

dates as (
    select cast(series_date as date) as date_key
    from bounds,
         generate_series(min_date, max_date, interval '1 day') as spine(series_date)
)

select
    date_key,
    extract('year' from date_key)::integer as year,
    extract('quarter' from date_key)::integer as quarter,
    extract('month' from date_key)::integer as month,
    strftime(date_key, '%B') as month_name,
    extract('dow' from date_key)::integer as day_of_week,
    strftime(date_key, '%A') as day_name,
    extract('dow' from date_key) in (0, 6) as is_weekend
from dates

