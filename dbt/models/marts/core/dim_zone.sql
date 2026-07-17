{{ config(materialized='table') }}

select
    zone_id,
    borough,
    zone_name,
    service_zone,
    is_airport_zone
from {{ ref('stg_tlc__taxi_zones') }}

