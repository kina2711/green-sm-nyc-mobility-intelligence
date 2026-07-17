with counts as (
    select
        (select count(*) from {{ ref('int_trips_conformed') }}) as intermediate_count,
        (select count(*) from {{ ref('fct_trips') }}) as fact_count
)

select * from counts where intermediate_count != fact_count

