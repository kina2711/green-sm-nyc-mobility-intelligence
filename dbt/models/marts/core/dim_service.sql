{{ config(materialized='table') }}

select distinct
    md5(concat_ws('|', service_type, operator)) as service_key,
    service_type,
    operator,
    service_category
from {{ ref('int_trips_conformed') }}

